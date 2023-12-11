import logging

class PriceDataError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UtilService:
    @staticmethod
    def validate_prices(prices, period):
        if len(prices) < period:
            raise PriceDataError(f"Não há dados suficientes para calcular o indicador. "
                                 f"Esperado: {period}, fornecido: {len(prices)}")

    @staticmethod
    def calculate_rsi(prices, period=14):
        if not prices or len(prices) < period:
            logging.warning("Dados insuficientes para calcular o RSI.")
            return None
        gains, losses = 0, 0
        for i in range(1, period + 1):
            difference = prices[i] - prices[i - 1]
            gains += max(difference, 0)
            losses -= min(difference, 0)
        avg_gain = gains / period if gains > 0 else 0
        avg_loss = -losses / period if losses < 0 else 0
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 100
        return rsi

    @staticmethod
    def calculate_ema(prices, period=9):
        if not prices or len(prices) < period:
            logging.warning("Dados insuficientes para calcular a EMA.")
            return None
        ema, multiplier = prices[0], 2 / (period + 1)
        for price in prices[1:]:
            ema = ((price - ema) * multiplier) + ema
        return ema

    @staticmethod
    def calculate_price_change(prices):
        if not prices or prices[0] == 0:
            raise PriceDataError("Preço inicial não pode ser zero para calcular a mudança de preço.")
        try:
            return ((prices[-1] - prices[0]) / prices[0]) * 100
        except Exception as e:
            logging.error(f"Erro ao calcular a mudança de preço: {e}")
            raise

    @staticmethod
    def calculate_stochastic_oscillator(prices, period=14):
        if not prices or len(prices) < period:
            logging.warning("Dados insuficientes para calcular o Oscilador Estocástico.")
            return None
        low, high = min(prices[:period]), max(prices[:period])
        if high == low:
            return 100
        return ((prices[-1] - low) / (high - low)) * 100

    @staticmethod
    def identify_patterns(prices):
        if not prices or len(prices) < 5:
            logging.warning("Dados insuficientes para identificar padrões.")
            return {'wPatterns': [], 'mPatterns': []}
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
        if not prices or len(prices) < 3:
            logging.warning("Dados insuficientes para calcular suporte e resistência.")
            return {'support': None, 'resistance': None}
        low, high, close = min(prices), max(prices), prices[-1]
        pivot_point = (low + high + close) / 3
        support = 2 * pivot_point - high
        resistance = 2 * pivot_point - low
        return {'support': support, 'resistance': resistance}

    @staticmethod
    def apply_retracement_strategy(prices, time_frame):
        levels = UtilService.calculate_support_and_resistance(prices)
        if not levels['support'] or not levels['resistance']:
            return "Sem sinal"
        current_price = prices[-1]
        if levels['support'] < current_price < levels['resistance']:
            return "Retrair" if time_frame in ['5min', '15min'] else "Sem sinal"
        return "Sem sinal"

    @staticmethod
    def apply_composite_retracement_strategy(prices_5min, prices_15min):
        retracement_5min = UtilService.apply_retracement_strategy(prices_5min, '5min')
        retracement_15min = UtilService.apply_retracement_strategy(prices_15min, '15min')
        if retracement_5min == "Retrair" and retracement_15min == "Retrair":
            return "Retração Forte"
        return "Sem sinal"
