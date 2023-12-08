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

        # Obtem os pesos do modelo de aprendizado
        weights = self.learning_service.get_weights()

        # Calcula os indicadores técnicos
        indicators = {
            "rsi": self.util_service.calculate_rsi(prices5min),
            "ema": self.util_service.calculate_ema(prices5min),
            "price_change": self.util_service.calculate_price_change(prices5min),
            "stochastic_oscillator": self.util_service.calculate_stochastic_oscillator(prices5min),
            "pattern": self.util_service.identify_patterns(prices5min)
        }

        # Obtem a decisão com base nos indicadores e pesos do modelo
        total_score = self.learning_service.make_decision(indicators)
        success = total_score > 0
        self.learning_service.store_result(indicators, success)

        # Interpreta a pontuação total para tomar uma decisão
        if total_score == 0:
            return 'Sem sinal'

        confidence = abs(total_score)
        decision = "Compra" if total_score > 0 else "Venda"
        decision += f" com {confidence * 10}% de confiança"
        return decision

    # Métodos para calcular os scores de cada indicador técnico
    # Aqui estou assumindo que você tem constantes definidas para os limites
    def get_rsi_score(self, rsi):
        return 1 if rsi < RSI_LOWER_LIMIT else -1 if rsi > RSI_UPPER_LIMIT else 0

    def get_ema_score(self, price, ema9):
        return 1 if price > ema9 else -1 if price < ema9 else 0

    def get_price_change_score(self, price_change):
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    def get_stochastic_oscillator_score(self, stochastic_oscillator):
        return 1 if stochastic_oscillator < STOCHASTIC_LOWER_LIMIT else -1 if stochastic_oscillator > STOCHASTIC_UPPER_LIMIT else 0

    def get_pattern_score(self, patterns):
        return 1 if 'bullish' in patterns else -1 if 'bearish' in patterns else 0

# Você precisa assegurar que os métodos de score estejam sendo chamados no make_decision se necessário,
# e que as constantes como RSI_LOWER_LIMIT, RSI_UPPER_LIMIT, etc., estão definidas em seu módulo constants.py.
