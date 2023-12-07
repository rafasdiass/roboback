# services/decision_service.py

from .util_service import UtilService
from .learning_service import LearningService
from .constants import *

class DecisionService:
    def __init__(self):
        self.util_service = UtilService()
        self.learning_service = LearningService()

    def make_decision(self, currency_pair, prices5min, prices15min, prices1h):
        if not prices5min:
            print("Dados de preços de 5 minutos insuficientes para tomar uma decisão.")
            return "Sem sinal"

        weights = self.learning_service.get_weights()
        indicators = {
            "rsi": self.get_rsi_score(self.util_service.calculate_rsi(prices5min)),
            "ema": self.get_ema_score(prices5min[0], self.util_service.calculate_ema(prices5min)),
            "price_change": self.get_price_change_score(self.util_service.calculate_price_change(prices5min)),
            "stochastic_oscillator": self.get_stochastic_oscillator_score(self.util_service.calculate_stochastic_oscillator(prices5min)),
            "fibonacci_level": self.get_fibonacci_level_score(prices5min[0], self.util_service.calculate_fibonacci_levels(min(prices5min), max(prices5min))),
            "pattern": self.get_pattern_score(self.util_service.identify_patterns(prices5min))
        }

        total_score = self.learning_service.make_decision(indicators)
        self.learning_service.store_result(indicators, total_score > 0)

        if total_score == 0:
            return 'Sem sinal'

        confidence = abs(total_score)
        decision = "Compra" if total_score > 0 else "Venda"
        decision += f" com {confidence * 10}% de confiança"
        return decision

    def get_rsi_score(self, rsi):
        return 1 if rsi < RSI_LOWER_LIMIT else -1 if rsi > RSI_UPPER_LIMIT else 0

    def get_ema_score(self, price, ema9):
        return 1 if price > ema9 else -1 if price < ema9 else 0

    def get_price_change_score(self, price_change):
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    def get_stochastic_oscillator_score(self, stochastic_oscillator):
        return 1 if stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else -1 if stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 0

    def get_fibonacci_level_score(self, price, fibonacci_levels):
        return 1 if fibonacci_levels[FIBONACCI_LOWER_LEVEL] < price < fibonacci_levels[FIBONACCI_UPPER_LEVEL] else 0

    def get_pattern_score(self, patterns):
        w_patterns, m_patterns = patterns['wPatterns'], patterns['mPatterns']
        last_index = len(w_patterns) - 1
        return 1 if last_index in w_patterns else -1 if last_index in m_patterns else 0
