import logging
from .util_service import UtilService, PriceDataError
from .learning_service import LearningService
from .constants import *

class DecisionService:
    def __init__(self):
        self.util_service = UtilService()
        self.learning_service = LearningService()

    def make_decision(self, currency_pair, prices5min, prices15min, prices1h):
        if not all(prices for prices in [prices5min, prices15min, prices1h]):
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
        price = prices[-1]  # Preço atual
        return {
            "price": price,
            "rsi": self.util_service.calculate_rsi(prices),
            "ema": self.util_service.calculate_ema(prices),
            "price_change": self.util_service.calculate_price_change(prices),
            "stochastic_oscillator": self.util_service.calculate_stochastic_oscillator(prices),
            "pattern": self.util_service.identify_patterns(prices)
        }

    def calculate_scores(self, indicators):
        return {
            'rsi_score': self.get_rsi_score(indicators['rsi']),
            'ema_score': self.get_ema_score(indicators['ema'], indicators['price']),
            'price_change_score': self.get_price_change_score(indicators['price_change']),
            'stochastic_oscillator_score': self.get_stochastic_oscillator_score(indicators['stochastic_oscillator']),
            'pattern_score': self.get_pattern_score(indicators['pattern'])
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
        # Uma decisão padrão em caso de dados insuficientes ou erros
        return "Manter"

    def get_rsi_score(self, rsi):
        if rsi is None:
            return 0
        return 1 if rsi < RSI_LOWER_LIMIT else -1 if rsi > RSI_UPPER_LIMIT else 0

    def get_ema_score(self, ema, price):
        if ema is None or price is None:
            return 0
        return 1 if price > ema else -1 if price < ema else 0

    def get_price_change_score(self, price_change):
        if price_change is None:
            return 0
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    def get_stochastic_oscillator_score(self, stochastic_oscillator):
        if stochastic_oscillator is None:
            return 0
        return 1 if stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else -1 if stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 0

    def get_pattern_score(self, pattern):
        if pattern is None:
            return 0
        return 1 if 'bullish' in pattern else -1 if 'bearish' in pattern else 0
