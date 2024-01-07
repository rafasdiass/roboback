
import logging
from automacao.models import Weight

class LearningService:
    def __init__(self):
        self.default_weights = {
            'rsi': 1,
            'ema': 1,
            'price_change': 1,
            'stochastic_oscillator': 1,
            'pattern': 1
        }
        self.weights = self.load_weights()  # Chamada síncrona aqui
        self.decay_factor = 0.9
        self.initial_learning_rate = 0.1
        self.learning_rate = self.initial_learning_rate
        self.learning_rate_decay = 0.99

    def load_weights(self):
        """ Carrega os pesos do banco de dados, usando pesos padrão em caso de falha. """
        weights = self.default_weights.copy()
        try:
            weight_objects = Weight.objects.all()  # Chamada síncrona aqui
            for weight_object in weight_objects:
                self.update_weight_from_object(weights, weight_object)
        except Exception as e:
            logging.error(f"Erro ao carregar pesos: {e}")
        return weights

    def update_weight_from_object(self, weights, weight_object):
        """ Atualiza os pesos com base no objeto de peso do banco de dados. """
        if -1 <= weight_object.value <= 1:
            weights[weight_object.indicator] = weight_object.value

    async def save_weights(self):
        """ Salva os pesos no banco de dados de forma assíncrona. """
        for key, value in self.weights.items():
            await self.update_and_save_weight(key, value)

    async def update_and_save_weight(self, key, value):
        """ Aplica o decaimento e salva o peso no banco de dados de forma assíncrona. """
        value = self.apply_decay(value)
        try:
            await Weight.objects.update_or_create(indicator=key, defaults={'value': value})
        except Exception as e:
            logging.error(f"Erro ao salvar pesos: {e}")

    def apply_decay(self, value):
        """ Aplica o fator de decaimento e limita o valor. """
        return max(min(value * self.decay_factor, 1), -1)

    async def store_result(self, indicators, success):
        """ Armazena o resultado do aprendizado de forma assíncrona, ajustando os pesos com base no sucesso. """
        self.adjust_weights_based_on_success(indicators, success)
        self.normalize_weights()
        await self.save_weights()
        self.learning_rate *= self.learning_rate_decay

    def adjust_weights_based_on_success(self, indicators, success):
        """ Ajusta os pesos com base no resultado do aprendizado. """
        for key in indicators:
            self.weights[key] = self.calculate_new_weight(key, success)

    def calculate_new_weight(self, key, success):
        """ Calcula o novo peso com base no sucesso do indicador. """
        delta = self.learning_rate if success else -self.learning_rate
        return max(min(self.weights.get(key, 0) + delta, 1), -1)

    def normalize_weights(self):
        """ Normaliza os pesos para garantir que a soma dos pesos absolutos seja 1. """
        sum_weights = sum(abs(weight) for weight in self.weights.values())
        for key in self.weights:
            self.weights[key] /= sum_weights

    async def get_weights(self):
        """ Retorna os pesos atuais de forma assíncrona. """
        if self.weights is None:
            await self.initialize_weights()
        return self.weights

    def reset_learning_rate(self):
        """ Reinicia a taxa de aprendizado para o valor inicial. """
        self.learning_rate = self.initial_learning_rate
