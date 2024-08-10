import logging
from collections import deque
from automacao.models import Weight

class LearningService:
    def __init__(self, window_size=5, long_term_decay_factor=0.95):
        self.default_weights = {
            'rsi': 1,
            'ema': 1,
            'price_change': 1,
            'stochastic_oscillator': 1,
            'pattern': 1,
            'ema_50_breakout_flow': 1
        }
        self.short_term_memory = {indicator: deque(maxlen=window_size) for indicator in self.default_weights.keys()}
        self.long_term_memory = self.default_weights.copy()
        self.long_term_decay_factor = long_term_decay_factor
        self.learning_rate = 0.1
        self.weights = self.combine_memories()

    def combine_memories(self):
        combined_weights = {}
        for key in self.short_term_memory.keys():
            short_term_avg = sum(self.short_term_memory[key]) / len(self.short_term_memory[key]) if self.short_term_memory[key] else 0
            combined_weights[key] = (
                0.7 * short_term_avg + 
                0.3 * self.long_term_memory[key]
            )
        return combined_weights

    def adjust_weights_based_on_success(self, indicators, success):
        """Ajusta os pesos com base no sucesso ou falha de uma decisão."""
        for key in indicators:
            self.short_term_memory[key].append(self.calculate_new_weight(self.short_term_memory[key][-1] if self.short_term_memory[key] else 0, success))
            self.long_term_memory[key] = self.calculate_new_weight(self.long_term_memory[key], success)

        self.apply_decay_to_long_term()
        self.weights = self.combine_memories()

    def apply_decay_to_long_term(self):
        """Aplica decaimento aos pesos de longo prazo."""
        for key in self.long_term_memory.keys():
            self.long_term_memory[key] *= self.long_term_decay_factor

    def calculate_new_weight(self, current_weight, success):
        """Calcula o novo peso para um indicador específico, baseado no sucesso."""
        delta = self.learning_rate if success else -self.learning_rate
        return max(min(current_weight * (1 - self.learning_rate) + delta, 1), -1)

    def normalize_weights(self):
        """Normaliza os pesos para garantir que a soma absoluta dos pesos seja 1."""
        sum_weights = sum(abs(weight) for weight in self.weights.values())
        if sum_weights == 0:  # Prevenção de divisão por zero
            return
        for key in self.weights:
            self.weights[key] /= sum_weights

    async def save_weights(self):
        """Salva os pesos atualizados no banco de dados."""
        for key, value in self.weights.items():
            await self.update_and_save_weight(key, value)

    async def update_and_save_weight(self, key, value):
        """Salva o peso no banco de dados."""
        try:
            await Weight.objects.update_or_create(indicator=key, defaults={'value': value})
        except Exception as e:
            logging.error(f"Erro ao salvar pesos: {e}")

    async def store_result(self, indicators, success):
        """Ajusta os pesos com base no resultado de uma decisão e salva as alterações."""
        self.adjust_weights_based_on_success(indicators, success)
        self.normalize_weights()
        await self.save_weights()

    async def get_weights(self):
        """Retorna os pesos atuais."""
        return self.weights
