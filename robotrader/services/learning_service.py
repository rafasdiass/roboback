# services/learning_service.py

class LearningService:
    def __init__(self):
        self.default_weights = {
            'rsi': 1,
            'ema': 1,
            'price_change': 1,
            'stochastic_oscillator': 1,
            'fibonacci_level': 1,
            'pattern': 1
        }
        self.weights = self.load_weights()
        self.decay_factor = 0.9
        self.learning_rate = 0.1

    def load_weights(self):
        # Aqui você pode carregar os pesos do banco de dados
        # Por simplicidade, estou usando os pesos padrão
        return self.default_weights.copy()

    def save_weights(self):
        for key in self.weights:
            self.weights[key] *= self.decay_factor
        # Aqui você pode salvar os pesos no banco de dados

    def store_result(self, indicators, success):
        for key in indicators:
            delta = self.learning_rate if success else -self.learning_rate
            self.weights[key] = self.weights.get(key, 0) + delta

        sum_weights = sum(self.weights.values())
        for key in self.weights:
            self.weights[key] /= sum_weights

        self.save_weights()

    def make_decision(self, indicators):
        score = 0
        for key, value in indicators.items():
            score += self.weights.get(key, 0) * value

        # Considerar a correlação entre diferentes indicadores
        if indicators.get('rsi', 0) > 0 and indicators.get('price_change', 0) < 0:
            score *= 0.9

        return score

    def get_weights(self):
        return self.weights
