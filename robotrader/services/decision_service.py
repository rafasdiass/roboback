import logging
from .util_service import UtilService, PriceDataError
from .learning_service import LearningService
from .constants import *

class DecisionService:
    def __init__(self):
        self.util_service = UtilService()
        self.learning_service = LearningService()

    def make_decision(self, currency_pair, prices5min, prices15min, prices1h):
        """
        Avalia a decisão de negociação com base em dados de preços e indicadores técnicos.
        """
        if not all([prices5min, prices15min, prices1h]):
            logging.warning(f"Dados de preços insuficientes ou nulos para {currency_pair}.")
            return "Sem sinal", None

        try:
            indicators = self.calculate_indicators(prices5min, prices15min, prices1h)
            scores = self.calculate_scores(indicators)
            decision, confidence = self.evaluate_decision(scores)
            return decision if decision != "Sem sinal" else self.default_decision(), indicators
        except Exception as e:
            logging.error(f"Erro no cálculo dos indicadores para {currency_pair}: {e}")
            return self.default_decision(), None

    def calculate_indicators(self, prices5min, prices15min, prices1h):
        """
        Calcula vários indicadores técnicos a partir dos dados de preços.
        """
        price = prices5min[-1]
        rsi, stochastic_oscillator = self.util_service.calculate_combined_stochastic_rsi(prices5min, prices5min, prices5min)
        adx = self.util_service.calculate_adx(prices5min, prices5min, prices5min)
        
        bollinger_bands_5min = self.util_service.calculate_bollinger_bands(prices5min)
        bollinger_bands_15min = self.util_service.calculate_bollinger_bands(prices15min)
        bollinger_bands_1h = self.util_service.calculate_bollinger_bands(prices1h)

        return {
            "price": price,
            "rsi": rsi,
            "stochastic_oscillator": stochastic_oscillator,
            "ema": self.util_service.calculate_ema(prices5min),
            "adx": adx,
            "price_change": self.util_service.calculate_price_change(prices5min),
            "pattern": self.util_service.identify_patterns(prices5min),
            "bollinger_bands_5min": bollinger_bands_5min,
            "bollinger_bands_15min": bollinger_bands_15min,
            "bollinger_bands_1h": bollinger_bands_1h
        }

    def calculate_scores(self, indicators):
        """
        Calcula as pontuações com base nos indicadores e na sua importância definida nos pesos.
        """
        adx_score = self.score_adx(indicators['adx'], indicators)

        return {
            'rsi_score': self.score_rsi(indicators['rsi']),
            'ema_score': self.score_ema(indicators['ema'], indicators['price']),
            'price_change_score': self.score_price_change(indicators['price_change']),
            'stochastic_oscillator_score': self.score_stochastic_oscillator(indicators['stochastic_oscillator'], indicators['rsi']),
            'pattern_score': self.score_pattern(indicators['pattern']),
            'bollinger_band_score': self.score_bollinger_bands(indicators['price'], indicators['bollinger_bands_5min']),
            'adx_score': adx_score
        }

    def evaluate_decision(self, scores):
        """
        Avalia a decisão de negociação com base nas pontuações calculadas.
        """
        weights = self.learning_service.get_weights()
        total_score = sum(weights[key] * score for key, score in scores.items())

        if total_score == 0:
            return 'Sem sinal', None

        confidence = abs(total_score)
        decision = "Compra" if total_score > 0 else "Venda"
        return f"{decision} com {confidence * 10:.0f}% de confiança", confidence

    def default_decision(self):
        """
        Retorna a decisão padrão quando não há sinal.
        """
        return "Manter"

    def score_rsi(self, rsi):
        """
        Calcula a pontuação para o RSI.
        """
        if rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT else 0

    def score_ema(self, ema, price):
        """
        Calcula a pontuação para a EMA.
        """
        if ema is None or price is None:
            return 0
        ema_direction, ema_touches = self.util_service.get_ema_direction_and_touches([price])
        if ema_touches >= 3:
            return 1 if price > ema and ema_direction == 'up' else -1 if price < ema and ema_direction == 'down' else 0
        return 0

    def score_price_change(self, price_change):
        """
        Calcula a pontuação para a mudança de preço.
        """
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    def score_stochastic_oscillator(self, stochastic_oscillator, rsi):
        """
        Calcula a pontuação para o Oscilador Estocástico.
        """
        if stochastic_oscillator is None or rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT and stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT and stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else 0

    def score_pattern(self, pattern):
        """
        Calcula a pontuação para os padrões identificados.
        """
        return 1 if 'bullish' in pattern else -1 if 'bearish' in pattern else 0

    def score_bollinger_bands(self, price, bollinger_bands):
        """
        Calcula a pontuação para as Bandas de Bollinger.
        """
        if bollinger_bands is None or price is None:
            return 0
        upper_band, _, lower_band = bollinger_bands
        return -1 if price > upper_band.iloc[-1] else 1 if price < lower_band.iloc[-1] else 0

    def score_adx(self, adx, indicators):
        """
        Calcula a pontuação para o ADX.
        """
        ADX_THRESHOLD = 25
        if adx is None:
            return 0

        trend_direction = self.determine_trend_direction(indicators)
        
        if adx > ADX_THRESHOLD and trend_direction != 'neutral':
            return 1 if trend_direction == 'up' else -1
        else:
            return 0

    def determine_trend_direction(self, indicators):
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
