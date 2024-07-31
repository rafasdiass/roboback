import pandas as pd
import numpy as np
import logging

class PriceDataError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UtilService:
    @staticmethod
    async def validate_prices(prices, period):
        if not isinstance(prices, pd.Series):
            raise PriceDataError("Preços devem ser uma série de números.")

        if len(prices) < period:
            raise PriceDataError(f"Não há dados suficientes para calcular o indicador. Esperado: {period}, fornecido: {len(prices)}")

    @staticmethod
    async def calculate_rsi(prices, period=7):
        await UtilService.validate_prices(prices, period + 1)

        delta = prices.diff().dropna()
        up, down = delta.clip(lower=0), -delta.clip(upper=0)

        roll_up = up.ewm(span=period).mean()
        roll_down = down.ewm(span=period).mean()

        RS = roll_up / roll_down
        return 100.0 - (100.0 / (1.0 + RS))

    @staticmethod
    async def calculate_stochastic_oscillator(high_prices, low_prices, close_prices, period=14):
        await UtilService.validate_prices(high_prices, period)
        await UtilService.validate_prices(low_prices, period)
        await UtilService.validate_prices(close_prices, period)

        high_max = high_prices.rolling(window=period).max()
        low_min = low_prices.rolling(window=period).min()

        return ((close_prices.iloc[-1] - low_min.iloc[-1]) / (high_max.iloc[-1] - low_min.iloc[-1])) * 100

    @staticmethod
    async def calculate_combined_stochastic_rsi(high_prices, low_prices, close_prices, rsi_period=7, stochastic_period=14):
        max_period = max(rsi_period, stochastic_period)
        await UtilService.validate_prices(close_prices, max_period)

        rsi = await UtilService.calculate_rsi(close_prices, rsi_period)
        stochastic = await UtilService.calculate_stochastic_oscillator(high_prices, low_prices, close_prices, stochastic_period)

        return rsi, stochastic

    @staticmethod
    async def calculate_ema(prices, period=9):
        await UtilService.validate_prices(prices, period)

        return prices.ewm(span=period, adjust=False).mean().iloc[-1]

    @staticmethod
    async def get_ema_direction_and_touches(prices, period=9):
        await UtilService.validate_prices(prices, period)

        ema = prices.ewm(span=period, adjust=False).mean()
        direction = "up" if ema.iloc[-1] > ema.iloc[-2] else "down"

        return direction, await UtilService.calculate_ema_touches(prices, ema)

    @staticmethod
    async def calculate_ema_touches(prices, ema, threshold=0.03):
        ema_touches = 0
        touch_flag = False

        for i in range(1, len(prices)):
            price_distance = abs(prices.iloc[i] - ema.iloc[i]) / ema.iloc[i]

            if price_distance <= threshold and not touch_flag:
                touch_flag = True
            elif touch_flag and ((prices.iloc[i] > ema.iloc[i] and prices.iloc[i-1] < ema.iloc[i-1]) or 
                                 (prices.iloc[i] < ema.iloc[i] and prices.iloc[i-1] > ema.iloc[i-1])):
                ema_touches += 1
                touch_flag = False

        return ema_touches

    @staticmethod
    async def calculate_price_change(prices):
        if prices.empty or prices.iloc[0] == 0:
            raise PriceDataError("Preço inicial não pode ser zero para calcular a mudança de preço.")

        try:
            return ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100
        except Exception as e:
            logging.error(f"Erro ao calcular a mudança de preço: {e}")
            raise

    @staticmethod
    async def identify_patterns(prices):
        if len(prices) < 5:
            logging.warning("Dados insuficientes para identificar padrões.")
            return {'topo_duplo': [], 'fundo_duplo': []}

        topo_duplo, fundo_duplo = [], []

        for i in range(4, len(prices)):
            segment = prices.iloc[i-4:i+1]
            if UtilService.is_double_top(segment):
                topo_duplo.append(i-2)
            if UtilService.is_double_bottom(segment):
                fundo_duplo.append(i-2)

        return {'topo_duplo': topo_duplo, 'fundo_duplo': fundo_duplo}

    @staticmethod
    def is_double_top(segment):
        return segment.iloc[1] == max(segment[:3]) and segment.iloc[3] == max(segment[2:])

    @staticmethod
    def is_double_bottom(segment):
        return segment.iloc[1] == min(segment[:3]) and segment.iloc[3] == min(segment[2:])

    @staticmethod
    async def calculate_support_and_resistance(prices):
        if len(prices) < 2:
            logging.warning("Dados insuficientes para calcular suporte e resistência.")
            return {'support': None, 'resistance': None}

        high = max(prices)
        low = min(prices)
        pivot_point = (high + low + prices.iloc[-1]) / 3

        return {'support': 2 * pivot_point - high, 'resistance': 2 * pivot_point - low}

    @staticmethod
    async def calculate_bollinger_bands(prices, period=20, num_std_dev=2):
        await UtilService.validate_prices(prices, period)

        sma = prices.rolling(window=period).mean()
        rstd = prices.rolling(window=period).std()

        upper_band = sma + rstd * num_std_dev
        lower_band = sma - rstd * num_std_dev

        return upper_band, sma, lower_band

    @staticmethod
    async def calculate_directional_movement(high_prices, low_prices):
        positive_movement = [max(0, high_prices.iloc[i] - high_prices.iloc[i - 1]) for i in range(1, len(high_prices))]
        negative_movement = [max(0, low_prices.iloc[i - 1] - low_prices.iloc[i]) for i in range(1, len(low_prices))]

        return positive_movement, negative_movement

    @staticmethod
    async def calculate_directional_indicators(high_prices, low_prices, close_prices, period):
        positive_movement, negative_movement = await UtilService.calculate_directional_movement(high_prices, low_prices)

        tr = [max(high_prices.iloc[i] - low_prices.iloc[i], abs(high_prices.iloc[i] - close_prices.iloc[i - 1]), abs(low_prices.iloc[i] - close_prices.iloc[i - 1])) for i in range(1, len(close_prices))]
        tr_smoothed = pd.Series(tr).rolling(window=period).sum()

        pdi = 100 * pd.Series(positive_movement).rolling(window=period).sum() / tr_smoothed
        ndi = 100 * pd.Series(negative_movement).rolling(window=period).sum() / tr_smoothed

        return pdi, ndi

    @staticmethod
    async def calculate_adx(high_prices, low_prices, close_prices, period=14):
        await UtilService.validate_prices(close_prices, period + 1)

        pdi, ndi = await UtilService.calculate_directional_indicators(high_prices, low_prices, close_prices, period)
        adx_series = (abs(pdi - ndi) / (pdi + ndi)).replace([np.inf, -np.inf], 0).fillna(0) * 100
        adx = adx_series.ewm(span=period, adjust=False).mean()

        return adx.iloc[-1]

    @staticmethod
    async def calculate_macd(prices, slow=26, fast=12, signal=9):
        await UtilService.validate_prices(prices, slow)

        fast_ema = prices.ewm(span=fast, adjust=False).mean()
        slow_ema = prices.ewm(span=slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal_line = macd.ewm(span=signal, adjust=False).mean()

        return macd.iloc[-1], signal_line.iloc[-1]
