# services/util_service.py

class PriceDataError(Exception):
    """Exceção personalizada para erros relacionados aos dados de preço."""
    def __init__(self, message):
        super().__init__(message)

class UtilService:
    @staticmethod
    def validate_prices(prices, period):
        """Garante que há dados suficientes para realizar os cálculos."""
        if len(prices) < period:
            raise PriceDataError(f"Não há dados suficientes para calcular o indicador. "
                                 f"Esperado: {period}, fornecido: {len(prices)}")

    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calcula o Índice de Força Relativa (RSI) para um conjunto de preços."""
        UtilService.validate_prices(prices, period)
        gains, losses = 0, 0
        for i in range(1, period + 1):
            difference = prices[i] - prices[i - 1]
            if difference > 0:
                gains += difference
            else:
                losses -= difference
        avg_gain, avg_loss = gains / period, losses / period
        rs = avg_gain / avg_loss if avg_loss else 0
        rsi = 100 - (100 / (1 + rs)) if avg_loss else 100
        return rsi

    @staticmethod
    def calculate_ema(prices, period=9):
        """Calcula a Média Móvel Exponencial (EMA) para um conjunto de preços."""
        UtilService.validate_prices(prices, period)
        ema, multiplier = prices[0], 2 / (period + 1)
        for price in prices[1:]:
            ema = ((price - ema) * multiplier) + ema
        return ema

    @staticmethod
    def calculate_sma(prices, period):
        """Calcula a Média Móvel Simples (SMA) para um conjunto de preços."""
        UtilService.validate_prices(prices, period)
        return sum(prices[:period]) / period

    @staticmethod
    def calculate_price_change(prices):
        """Calcula a porcentagem de mudança do preço."""
        if not prices or prices[0] == 0:
            raise PriceDataError("Preço inicial não pode ser zero para calcular a mudança de preço.")
        return ((prices[-1] - prices[0]) / prices[0]) * 100

    @staticmethod
    def calculate_stochastic_oscillator(prices, period=14):
        """Calcula o Oscilador Estocástico para um conjunto de preços."""
        UtilService.validate_prices(prices, period)
        low, high = min(prices[:period]), max(prices[:period])
        if high == low:
            return 100  # Evita divisão por zero se todos os preços são iguais
        return ((prices[0] - low) / (high - low)) * 100

    @staticmethod
    def calculate_fibonacci_levels(low, high):
        """Calcula os níveis de retração de Fibonacci."""
        if low > high:
            raise ValueError("O valor 'low' deve ser menor que o valor 'high'.")
        diff = high - low
        return {
            '0.0%': low,
            '23.6%': low + diff * 0.236,
            '38.2%': low + diff * 0.382,
            '50.0%': low + diff * 0.5,
            '61.8%': low + diff * 0.618,
            '100.0%': high
        }

    @staticmethod
    def identify_patterns(prices):
        """Identifica padrões comuns de gráficos de preço."""
        UtilService.validate_prices(prices, 5)  # Necessário pelo menos 5 preços para identificar padrões
        w_patterns, m_patterns = [], []
        for i in range(4, len(prices)):
            slice = prices[i - 4:i + 1]
            if slice[0] > slice[1] < slice[2] > slice[3] < slice[4]:
                w_patterns.append(i)
            elif slice[0] < slice[1] > slice[2] < slice[3] > slice[4]:
                m_patterns.append(i)
        return {'wPatterns': w_patterns, 'mPatterns': m_patterns}

    @staticmethod
    def calculate_support_and_resistance(prices):
        """Calcula os níveis de suporte e resistência com base nos preços."""
        UtilService.validate_prices(prices, 3)  # Necessário pelo menos 3 preços para calcular
        low, high, close = min(prices), max(prices), prices[0]
        pivot_point = (low + high + close) / 3
        support = 2 * pivot_point - high
        resistance = 2 * pivot_point - low
        return {'support': support, 'resistance': resistance}

    @staticmethod
    def apply_retracement_strategy(prices, time_frame):
        """Aplica uma estratégia de retração com base em suporte e resistência."""
        levels = UtilService.calculate_support_and_resistance(prices)
        current_price = prices[0]
        if levels['support'] < current_price < levels['resistance']:
            return "Retrair" if time_frame in ['5min', '15min'] else "Sem sinal"
        return "Sem sinal"

    @staticmethod
    def apply_composite_retracement_strategy(prices_5min, prices_15min):
        """Combina estratégias de retração para diferentes períodos de tempo."""
        retracement_5min = UtilService.apply_retracement_strategy(prices_5min, '5min')
        retracement_15min = UtilService.apply_retracement_strategy(prices_15min, '15min')
        if retracement_5min == "Retrair" and retracement_15min == "Retrair":
            return "Retração Forte"
        return "Sem sinal"
