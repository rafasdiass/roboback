import logging
from .util_service import UtilService, PriceDataError
from .learning_service import LearningService
from .constants import *

class DecisionService:
    def __init__(self):
        self.util_service = UtilService()
        self.learning_service = LearningService()

    def make_decision(self, currency_pair, prices5min, prices15min, prices1h):
        if not all([prices5min, prices15min, prices1h]):
            logging.warning(f"Dados de preços insuficientes ou nulos para {currency_pair}.")
            return "Sem sinal", None

        try:
            indicators = self.calculate_indicators(prices5min)
            scores = self.calculate_scores(indicators)
            decision, confidence = self.evaluate_decision(scores)
            return decision if decision != "Sem sinal" else self.default_decision(), indicators
        except Exception as e:
            logging.error(f"Erro no cálculo dos indicadores para {currency_pair}: {e}")
            return self.default_decision(), None

    def calculate_indicators(self, prices):
        if not prices:
            raise PriceDataError("Lista de preços vazia.")

        price = prices[-1]
        rsi, stochastic_oscillator = self.util_service.calculate_combined_stochastic_rsi(prices, prices, prices)
        
        return {
            "price": price,
            "rsi": rsi,
            "stochastic_oscillator": stochastic_oscillator,
            "ema": self.util_service.calculate_ema(prices),
            "price_change": self.util_service.calculate_price_change(prices),
            "pattern": self.util_service.identify_patterns(prices),
            "bollinger_bands": self.util_service.calculate_bollinger_bands(prices)
        }

    def calculate_scores(self, indicators):
        return {
            'rsi_score': self.score_rsi(indicators['rsi']),
            'ema_score': self.score_ema(indicators['ema'], indicators['price']),
            'price_change_score': self.score_price_change(indicators['price_change']),
            'stochastic_oscillator_score': self.score_stochastic_oscillator(indicators['stochastic_oscillator'], indicators['rsi']),
            'pattern_score': self.score_pattern(indicators['pattern']),
            'bollinger_band_score': self.score_bollinger_bands(indicators['price'], indicators['bollinger_bands'])
        }

    def evaluate_decision(self, scores):
        weights = self.learning_service.get_weights()
        total_score = sum(weights[key] * score for key, score in scores.items())

        if total_score == 0:
            return 'Sem sinal', None

        confidence = abs(total_score)
        decision = "Compra" if total_score > 0 else "Venda"
        return f"{decision} com {confidence * 10:.0f}% de confiança", confidence

    def default_decision(self):
        return "Manter"

    def score_rsi(self, rsi):
        if rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT else 0

    def score_ema(self, ema, price):
        if ema is None or price is None:
            return 0
        ema_direction, ema_touches = self.util_service.get_ema_direction_and_touches([price])
        if ema_touches >= 3:
            return 1 if price > ema and ema_direction == 'up' else -1 if price < ema and ema_direction == 'down' else 0
        return 0

    def score_price_change(self, price_change):
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    def score_stochastic_oscillator(self, stochastic_oscillator, rsi):
        if stochastic_oscillator is None or rsi is None:
            return 0
        return -1 if rsi > RSI_UPPER_LIMIT and stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 1 if rsi < RSI_LOWER_LIMIT and stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else 0

    def score_pattern(self, pattern):
        return 1 if 'bullish' in pattern else -1 if 'bearish' in pattern else 0

    def score_bollinger_bands(self, price, bollinger_bands):
        if bollinger_bands is None or price is None:
            return 0
        upper_band, _, lower_band = bollinger_bands
        return -1 if price > upper_band.iloc[-1] else 1 if price < lower_band.iloc[-1] else 0
