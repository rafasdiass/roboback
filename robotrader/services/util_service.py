import pandas as pd
import numpy as np
import logging

class PriceDataError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UtilService:
    @staticmethod
    def validate_prices(prices, period):
        if len(prices) < period:
            raise PriceDataError(f"Não há dados suficientes para calcular o indicador. Esperado: {period}, fornecido: {len(prices)}")

    @staticmethod
    def calculate_rsi(prices, period=7):
        if len(prices) < period + 1:
            logging.warning("Dados insuficientes para calcular o RSI.")
            return None

        prices_series = pd.Series(prices)
        delta = prices_series.diff().dropna()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        roll_up = up.ewm(span=period).mean()
        roll_down = down.abs().ewm(span=period).mean()

        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))

        return RSI.iloc[-1]

    @staticmethod
    def calculate_stochastic_oscillator(high_prices, low_prices, close_prices, period=14):
        if len(close_prices) < period:
            logging.warning("Dados insuficientes para calcular o Oscilador Estocástico.")
            return None

        high_max = pd.Series(high_prices).rolling(window=period).max()
        low_min = pd.Series(low_prices).rolling(window=period).min()
        stoch = ((close_prices[-1] - low_min[-1]) / (high_max[-1] - low_min[-1])) * 100

        return stoch

    @staticmethod
    def calculate_combined_stochastic_rsi(high_prices, low_prices, close_prices, rsi_period=7, stochastic_period=14):
        if len(close_prices) < max(rsi_period, stochastic_period):
            logging.warning("Dados insuficientes para calcular o Stochastic RSI.")
            return None, None

        rsi = UtilService.calculate_rsi(close_prices, rsi_period)
        stochastic = UtilService.calculate_stochastic_oscillator(high_prices, low_prices, close_prices, stochastic_period)

        return rsi, stochastic

    @staticmethod
    def calculate_ema(prices, period=9):
        if len(prices) < period:
            logging.warning("Dados insuficientes para calcular a EMA.")
            return None

        prices_series = pd.Series(prices)
        ema = prices_series.ewm(span=period, adjust=False).mean()

        return ema.iloc[-1]

    @staticmethod
    def get_ema_direction_and_touches(prices, period=9):
        if len(prices) < period:
            return None, 0

        prices_series = pd.Series(prices)
        ema = prices_series.ewm(span=period, adjust=False).mean()
        direction = "up" if ema.iloc[-1] > ema.iloc[-2] else "down"

        ema_touches = UtilService.calculate_ema_touches(prices_series, ema)

        return direction, ema_touches

    @staticmethod
    def calculate_ema_touches(prices_series, ema_series, threshold=0.03):
        ema_touches = 0
        touch_flag = False

        for i in range(1, len(prices_series)):
            price_distance = abs(prices_series[i] - ema_series[i]) / ema_series[i]

            if price_distance <= threshold:
                if not touch_flag:
                    touch_flag = True  # Identifica o início de um toque
                    continue

            if touch_flag:
                if (prices_series[i] > prices_series[i-1] and prices_series[i-1] < ema_series[i-1]) or \
                   (prices_series[i] < prices_series[i-1] and prices_series[i-1] > ema_series[i-1]):
                    ema_touches += 1
                    touch_flag = False

        return ema_touches

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
    def identify_patterns(prices):
        if len(prices) < 5:
            logging.warning("Dados insuficientes para identificar padrões.")
            return {'topo_duplo': [], 'fundo_duplo': []}

        topo_duplo, fundo_duplo = [], []

        for i in range(4, len(prices)):
            segment = prices[i-4:i+1]
            if segment[1] == max(segment[:3]) and segment[3] == max(segment[2:]):
                topo_duplo.append(i-2)
            if segment[1] == min(segment[:3]) and segment[3] == min(segment[2:]):
                fundo_duplo.append(i-2)

        return {'topo_duplo': topo_duplo, 'fundo_duplo': fundo_duplo}

    @staticmethod
    def calculate_support_and_resistance(prices):
        if len(prices) < 2:
            logging.warning("Dados insuficientes para calcular suporte e resistência.")
            return {'support': None, 'resistance': None}

        high = max(prices)
        low = min(prices)
        pivot_point = (high + low + prices[-1]) / 3
        support = 2 * pivot_point - high
        resistance = 2 * pivot_point - low

        return {'support': support, 'resistance': resistance}

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, num_std_dev=2):
        if len(prices) < period:
            logging.warning("Dados insuficientes para calcular as Bandas de Bollinger.")
            return None, None, None

        prices_series = pd.Series(prices)
        sma = prices_series.rolling(window=period).mean()
        rstd = prices_series.rolling(window=period).std()

        upper_band = sma + rstd * num_std_dev
        lower_band = sma - rstd * num_std_dev

        return upper_band, sma, lower_band
