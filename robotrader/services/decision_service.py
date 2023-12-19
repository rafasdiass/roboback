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
        price = prices[-1]
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
            'ema_score': self.get_ema_score(indicators['ema'], indicators['price'], indicators['prices']),
            'price_change_score': self.get_price_change_score(indicators['price_change']),
            'stochastic_oscillator_score': self.get_stochastic_oscillator_score(indicators['stochastic_oscillator'], indicators['rsi']),
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
        return "Manter"

    def get_rsi_score(self, rsi):
        if rsi is None:
            return 0
        if rsi > RSI_UPPER_LIMIT:  # RSI_UPPER_LIMIT definido como 70
            return -1  # Pontuação para condição de sobrecompra (venda)
        elif rsi < RSI_LOWER_LIMIT:  # RSI_LOWER_LIMIT definido como 20
            return 1  # Pontuação para condição de sobrevenda (compra)
        else:
            return 0  # Neutro

    def get_ema_score(self, ema, price, prices):
        if ema is None or price is None:
            return 0

        # Lógica para determinar a direção da EMA e verificar os 3 toques com retração
        # Nota: Esta função precisa ser implementada em UtilService
        ema_direction, ema_touches = self.util_service.get_ema_direction_and_touches(prices)
        if ema_touches >= 3:
            if price > ema and ema_direction == 'up':
                return 1  # Tendência de alta confirmada
            elif price < ema and ema_direction == 'down':
                return -1  # Tendência de baixa confirmada
        return 0  # Neutro

    def get_price_change_score(self, price_change):
        if price_change is None:
            return 0
        return 1 if price_change > 0 else -1 if price_change < 0 else 0

    def get_stochastic_oscillator_score(self, stochastic_oscillator, rsi):
        if stochastic_oscillator is None or rsi is None:
            return 0

        # Uso do Oscilador Estocástico em conjunto com o RSI para confirmar tendências
        if rsi > RSI_UPPER_LIMIT and stochastic_oscillator > STOCHASTIC_UPPER_LIMIT:
            return -1  # Ambos indicam sobrecompra
        elif rsi < RSI_LOWER_LIMIT and stochastic_oscillator < STOCHASTIC_LOWER_LIMIT:
            return 1  # Ambos indicam sobrevenda
        return 0  # Neutro

    def get_pattern_score(self, pattern):
        if pattern is None:
            return 0
        return 1 if 'bullish' in pattern else -1 if 'bearish' in pattern else 0
