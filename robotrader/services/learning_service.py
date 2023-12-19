from automacao.models import Weight
import logging

class LearningService:
    def __init__(self):
        self.default_weights = {
            'rsi': 1,
            'ema': 1,
            'price_change': 1,
            'stochastic_oscillator': 1,
            'pattern': 1
        }
        self.weights = self.load_weights()
        self.decay_factor = 0.9
        self.initial_learning_rate = 0.1
        self.learning_rate = self.initial_learning_rate
        self.learning_rate_decay = 0.99

    def load_weights(self):
        weights = self.default_weights.copy()
        try:
            weight_objects = Weight.objects.all()
            for weight_object in weight_objects:
                if -1 <= weight_object.value <= 1:  # Validação de pesos
                    weights[weight_object.indicator] = weight_object.value
        except Exception as e:
            logging.error(f"Erro ao carregar pesos: {e}")
        return weights

    def save_weights(self):
        for key, value in self.weights.items():
            value *= self.decay_factor  # Aplica o fator de decaimento
            value = max(min(value, 1), -1)  # Garante que os pesos estejam no intervalo [-1, 1]
            try:
                Weight.objects.update_or_create(indicator=key, defaults={'value': value})
            except Exception as e:
                logging.error(f"Erro ao salvar pesos: {e}")

    def store_result(self, indicators, success):
        for key in indicators:
            delta = self.learning_rate if success else -self.learning_rate
            self.weights[key] = max(min(self.weights.get(key, 0) + delta, 1), -1)

        sum_weights = sum(abs(weight) for weight in self.weights.values())
        for key in self.weights:
            self.weights[key] /= sum_weights  # Normalização dos pesos

        self.save_weights()
        self.learning_rate *= self.learning_rate_decay  # Decaimento da taxa de aprendizado

    def get_weights(self):
        return self.weights

    def reset_learning_rate(self):
        self.learning_rate = self.initial_learning_rate
