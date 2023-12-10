from automacao.models import Weight
import random

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
        self.initial_learning_rate = 0.1
        self.learning_rate = self.initial_learning_rate
        self.learning_rate_decay = 0.99  # Decremento da taxa de aprendizado

    def load_weights(self):
        # Carrega os pesos do banco de dados
        weights = self.default_weights.copy()
        weight_objects = Weight.objects.all()
        for weight_object in weight_objects:
            weights[weight_object.indicator] = weight_object.value
        return weights

    def save_weights(self):
        # Salva os pesos no banco de dados
        for key, value in self.weights.items():
            Weight.objects.update_or_create(
                indicator=key, defaults={'value': value * self.decay_factor}
            )

    def store_result(self, indicators, success):
        # Atualiza os pesos com base no sucesso ou fracasso e salva no banco de dados
        for key in indicators:
            delta = self.learning_rate if success else -self.learning_rate
            self.weights[key] = max(min(self.weights.get(key, 0) + delta, 1), -1)  # Limita os pesos entre -1 e 1

        # Normaliza os pesos para que sua soma seja 1
        sum_weights = sum(abs(weight) for weight in self.weights.values())
        for key in self.weights:
            self.weights[key] /= sum_weights

        self.save_weights()

        # Reduz a taxa de aprendizado a cada iteração
        self.learning_rate *= self.learning_rate_decay

    def make_decision(self, indicators):
        # Faz uma decisão com base nos indicadores e pesos atuais
        score = 0
        for key, value in indicators.items():
            score += self.weights.get(key, 0) * value

        # Ajusta a pontuação se necessário com base na correlação dos indicadores
        if indicators.get('rsi', 0) > 0 and indicators.get('price_change', 0) < 0:
            score *= 0.9

        return score

    def get_weights(self):
        # Retorna os pesos atuais
        return self.weights

    # Função adicional para resetar a taxa de aprendizado (se necessário)
    def reset_learning_rate(self):
        self.learning_rate = self.initial_learning_rate
