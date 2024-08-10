import logging
import asyncio
from util_service import UtilService
from indicator_service import Indicator
from .learning_service import LearningService
from .constants import *
from automacao.models import DecisionRecord
import datetime

class DecisionService:
    def __init__(self, window_size=5, long_term_decay_factor=0.95):
        self.util_service = UtilService()
        self.learning_service = LearningService(window_size=window_size, long_term_decay_factor=long_term_decay_factor)

    async def make_decision(self, currency_pair, prices5min, prices15min, prices1h):
        if not all([not prices5min.empty, not prices15min.empty, not prices1h.empty]):
            logging.warning(f"Dados de preços insuficientes ou nulos para {currency_pair}.")
            return "Sem sinal", None

        try:
            indicators = await self.calculate_indicators(prices5min, prices15min, prices1h)
            scores = await self.calculate_scores(indicators)
            decision, confidence = await self.evaluate_decision(scores)

            result = await self.check_decision_result(currency_pair, decision)
            await self.learning_service.store_result(indicators, result)
            await self.record_decision(currency_pair, decision, result)

            return decision if decision != "Sem sinal" else await self.default_decision(), indicators
        except Exception as e:
            logging.error(f"Erro no cálculo dos indicadores para {currency_pair}: {e}")
            return await self.default_decision(), None

    async def calculate_indicators(self, prices5min, prices15min, prices1h):
        price = prices5min['Close'].iloc[-1]
        rsi, stochastic_oscillator = self.util_service.calculate_combined_stochastic_rsi(
            prices5min['High'], prices5min['Low'], prices5min['Close']
        )
        adx = self.util_service.calculate_adx(prices5min['High'], prices5min['Low'], prices5min['Close'])

        bollinger_bands_5min = Indicator.calculate_bollinger_bands(prices5min['Close'])
        bollinger_bands_15min = Indicator.calculate_bollinger_bands(prices15min['Close'])
        bollinger_bands_1h = Indicator.calculate_bollinger_bands(prices1h['Close'])

        # Verificação de rompimento da EMA 50 e continuidade do fluxo
        ema_50_breakout_flow = self.util_service.check_ema_50_breakout_and_flow(prices5min['Close'])

        return {
            "price": price,
            "rsi": rsi,
            "stochastic_oscillator": stochastic_oscillator,
            "ema": Indicator.calculate_ema(prices5min['Close']),
            "adx": adx,
            "price_change": self.util_service.calculate_price_change(prices5min['Close']),
            "pattern": self.util_service.identify_patterns(prices5min['Close']),
            "bollinger_bands_5min": bollinger_bands_5min,
            "bollinger_bands_15min": bollinger_bands_15min,
            "bollinger_bands_1h": bollinger_bands_1h,
            "ema_50_breakout_flow": ema_50_breakout_flow  # Adicionando o novo indicador
        }

    async def calculate_scores(self, indicators):
        adx_score = await self.score_adx(indicators['adx'], indicators)
        ema_50_breakout_flow_score = 1 if indicators['ema_50_breakout_flow'] else 0

        return {
            'rsi_score': await self.score_rsi(indicators['rsi']),
            'ema_score': await self.score_ema(indicators['ema'], indicators['price']),
            'price_change_score': await self.score_price_change(indicators['price_change']),
            'stochastic_oscillator_score': await self.score_stochastic_oscillator(indicators['stochastic_oscillator'], indicators['rsi']),
            'pattern_score': await self.score_pattern(indicators['pattern']),
            'bollinger_band_score': await self.score_bollinger_bands(indicators['price'], indicators['bollinger_bands_5min']),
            'adx_score': adx_score,
            'ema_50_breakout_flow_score': ema_50_breakout_flow_score  # Adicionando a pontuação do rompimento EMA 50
        }

    async def evaluate_decision(self, scores):
        weights = await self.learning_service.get_weights()
        total_score = sum(weights[key] * score for key, score in scores.items())

        if total_score == 0:
            return 'Sem sinal', None

        confidence = abs(total_score)
        decision = "Compra" if total_score > 0 else "Venda"
        return f"{decision} com {confidence * 10:.0f}% de confiança", confidence

    async def default_decision(self):
        return "Manter"

    async def score_rsi(self, rsi):
        if rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT else 0

    async def score_ema(self, ema, price):
        if ema is None or price is None:
            return 0
        ema_direction, ema_touches = self.util_service.get_ema_direction_and_touches([price])
        if ema_touches >= 3:
            return 1 if price > ema and ema_direction == 'up' else -1 if price < ema and ema_direction == 'down' else 0
        return 0

    async def score_price_change(self, price_change):
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    async def score_stochastic_oscillator(self, stochastic_oscillator, rsi):
        if stochastic_oscillator is None or rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT and stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT and stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else 0

    async def score_pattern(self, pattern):
        return 1 if 'bullish' in pattern else -1 if 'bearish' in pattern else 0

    async def score_bollinger_bands(self, price, bollinger_bands):
        if bollinger_bands is None or price is None:
            return 0
        upper_band, _, lower_band = bollinger_bands
        return -1 if price > upper_band.iloc[-1] else 1 if price < lower_band.iloc[-1] else 0

    async def score_adx(self, adx, indicators):
        ADX_THRESHOLD = 25
        if adx is None:
            return 0

        trend_direction = await self.determine_trend_direction(indicators)
        
        if adx > ADX_THRESHOLD and trend_direction != 'neutral':
            return 1 if trend_direction == 'up' else -1
        else:
            return 0

    async def determine_trend_direction(self, indicators):
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
        try:
            await asyncio.sleep(24 * 60 * 60)

            current_price = await self.util_service.get_current_price(currency_pair)
            decision_price = await self.util_service.get_price_at_time(currency_pair, datetime.datetime.now() - datetime.timedelta(days=1))

            if decision == "Compra":
                return current_price > decision_price
            elif decision == "Venda":
                return current_price < decision_price
            else:
                return False
        except Exception as e:
            logging.error(f"Erro ao verificar o resultado da decisão para {currency_pair}: {e}")
            return False

    async def record_decision(self, currency_pair, decision, result):
        try:
            DecisionRecord.objects.create(
                currency_pair=currency_pair,
                decision=decision,
                result=result
            )
        except Exception as e:
            logging.error(f"Erro ao registrar a decisão para {currency_pair}: {e}")
