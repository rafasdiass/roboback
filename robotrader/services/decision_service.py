import logging
import asyncio  # Importa o módulo asyncio
import datetime  # Importa o módulo datetime
from .util_service import UtilService  # Assumindo que UtilService é assíncrono
from .learning_service import LearningService  # Assumindo que LearningService também é assíncrono
from .constants import *  # Importando as constantes
from automacao.models import DecisionRecord  # Modelo para registrar decisões



class DecisionService:
    def __init__(self):
        self.util_service = UtilService()
        self.learning_service = LearningService()

    async def make_decision(self, currency_pair, prices5min, prices15min, prices1h):
        """
        Avalia a decisão de negociação com base em dados de preços e indicadores técnicos.
        """
        if not all([prices5min, prices15min, prices1h]):
            logging.warning(f"Dados de preços insuficientes ou nulos para {currency_pair}.")
            return "Sem sinal", None

        try:
            indicators = await self.calculate_indicators(prices5min, prices15min, prices1h)
            scores = await self.calculate_scores(indicators)
            decision, confidence = await self.evaluate_decision(scores)

            # Verifica e registra o resultado da decisão
            result = await self.check_decision_result(currency_pair, decision)
            await self.learning_service.store_result(indicators, result)
            await self.record_decision(currency_pair, decision, result)

            return decision if decision != "Sem sinal" else await self.default_decision(), indicators
        except Exception as e:
            logging.error(f"Erro no cálculo dos indicadores para {currency_pair}: {e}")
            return await self.default_decision(), None

    async def calculate_indicators(self, prices5min, prices15min, prices1h):
        """
        Calcula vários indicadores técnicos a partir dos dados de preços.
        """
        price = prices5min[-1]
        rsi, stochastic_oscillator = await self.util_service.calculate_combined_stochastic_rsi(prices5min, prices15min, prices1h)
        adx = await self.util_service.calculate_adx(prices5min, prices15min, prices1h)
        
        bollinger_bands_5min = await self.util_service.calculate_bollinger_bands(prices5min)
        bollinger_bands_15min = await self.util_service.calculate_bollinger_bands(prices15min)
        bollinger_bands_1h = await self.util_service.calculate_bollinger_bands(prices1h)

        return {
            "price": price,
            "rsi": rsi,
            "stochastic_oscillator": stochastic_oscillator,
            "ema": await self.util_service.calculate_ema(prices5min),
            "adx": adx,
            "price_change": await self.util_service.calculate_price_change(prices5min),
            "pattern": await self.util_service.identify_patterns(prices5min),
            "bollinger_bands_5min": bollinger_bands_5min,
            "bollinger_bands_15min": bollinger_bands_15min,
            "bollinger_bands_1h": bollinger_bands_1h
        }

    async def calculate_scores(self, indicators):
        """
        Calcula as pontuações com base nos indicadores e na sua importância definida nos pesos.
        """
        adx_score = await self.score_adx(indicators['adx'], indicators)

        return {
            'rsi_score': await self.score_rsi(indicators['rsi']),
            'ema_score': await self.score_ema(indicators['ema'], indicators['price']),
            'price_change_score': await self.score_price_change(indicators['price_change']),
            'stochastic_oscillator_score': await self.score_stochastic_oscillator(indicators['stochastic_oscillator'], indicators['rsi']),
            'pattern_score': await self.score_pattern(indicators['pattern']),
            'bollinger_band_score': await self.score_bollinger_bands(indicators['price'], indicators['bollinger_bands_5min']),
            'adx_score': adx_score
        }

    async def evaluate_decision(self, scores):
        """
        Avalia a decisão de negociação com base nas pontuações calculadas.
        """
        weights = await self.learning_service.get_weights()
        total_score = sum(weights[key] * score for key, score in scores.items())

        if total_score == 0:
            return 'Sem sinal', None

        confidence = abs(total_score)
        decision = "Compra" if total_score > 0 else "Venda"
        return f"{decision} com {confidence * 10:.0f}% de confiança", confidence

    async def default_decision(self):
        """
        Retorna a decisão padrão quando não há sinal.
        """
        return "Manter"

    async def score_rsi(self, rsi):
        """
        Calcula a pontuação para o RSI.
        """
        if rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT else 0

    async def score_ema(self, ema, price):
        """
        Calcula a pontuação para a EMA.
        """
        if ema is None or price is None:
            return 0
        ema_direction, ema_touches = await self.util_service.get_ema_direction_and_touches([price])
        if ema_touches >= 3:
            return 1 if price > ema and ema_direction == 'up' else -1 if price < ema and ema_direction == 'down' else 0
        return 0

    async def score_price_change(self, price_change):
        """
        Calcula a pontuação para a mudança de preço.
        """
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    async def score_stochastic_oscillator(self, stochastic_oscillator, rsi):
        """
        Calcula a pontuação para o Oscilador Estocástico.
        """
        if stochastic_oscillator is None or rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT and stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT and stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else 0

    async def score_pattern(self, pattern):
        """
        Calcula a pontuação para os padrões identificados.
        """
        return 1 if 'bullish' in pattern else -1 if 'bearish' in pattern else 0

    async def score_bollinger_bands(self, price, bollinger_bands):
        """
        Calcula a pontuação para as Bandas de Bollinger.
        """
        if bollinger_bands is None or price is None:
            return 0
        upper_band, _, lower_band = bollinger_bands
        return -1 if price > upper_band.iloc[-1] else 1 if price < lower_band.iloc[-1] else 0

    async def score_adx(self, adx, indicators):
        """
        Calcula a pontuação para o ADX.
        """
        ADX_THRESHOLD = 25
        if adx is None:
            return 0

        trend_direction = await self.determine_trend_direction(indicators)
        
        if adx > ADX_THRESHOLD and trend_direction != 'neutral':
            return 1 if trend_direction == 'up' else -1
        else:
            return 0

    async def determine_trend_direction(self, indicators):
        """
        Determina a direção da tendência com base em EMA e RSI.
        """
        ema = indicators['ema']
        price = indicators['price']
        rsi = indicators['rsi']

        if price > ema and rsi > 70:
            return 'up'
        elif price < ema and rsi < 30:
            return 'down'
        else:
            return 'neutral'

    async def check_decision_result(self, currency_pair, decision):
        """
        Verifica o resultado de uma decisão após um período de tempo.
        Retorna True para decisão bem-sucedida, False para mal-sucedida.
        """
        try:
            # Tempo de espera antes de verificar o resultado da decisão (ex: 24 horas)
            await asyncio.sleep(24 * 60 * 60) 

            # Obter os dados de mercado atuais
            current_price = await self.util_service.get_current_price(currency_pair)
            
            # Obter o preço no momento da decisão
            decision_price = await self.util_service.get_price_at_time(currency_pair, datetime.datetime.now() - datetime.timedelta(days=1))

            if decision == "Compra":
                # Se o preço subiu desde a decisão, então foi um sucesso
                return current_price > decision_price
            elif decision == "Venda":
                # Se o preço caiu desde a decisão, então foi um sucesso
                return current_price < decision_price
            else:
                # Se não houve sinal, não podemos determinar o sucesso
                return False
        except Exception as e:
            logging.error(f"Erro ao verificar o resultado da decisão para {currency_pair}: {e}")
            return False
    async def record_decision(self, currency_pair, decision, result):
        """
        Registra a decisão e seu resultado no banco de dados.
        """
        try:
            DecisionRecord.objects.create(
                currency_pair=currency_pair,
                decision=decision,
                result=result
            )
        except Exception as e:
            logging.error(f"Erro ao registrar a decisão para {currency_pair}: {e}")
