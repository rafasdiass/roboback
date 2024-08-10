import pandas as pd
import numpy as np

class PriceDataError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Indicator:
    @staticmethod
    def calculate_sma(prices, period):
        return prices.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(prices, period):
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(prices, period=7):
        delta = prices.diff().dropna()
        up, down = delta.clip(lower=0), -delta.clip(upper=0)
        roll_up = up.ewm(span=period, adjust=False).mean()
        roll_down = down.ewm(span=period, adjust=False).mean()
        RS = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + RS))
        return rsi

    @staticmethod
    def calculate_stochastic_oscillator(high_prices, low_prices, close_prices, period=14):
        high_max = high_prices.rolling(window=period).max()
        low_min = low_prices.rolling(window=period).min()
        stochastic = ((close_prices - low_min) / (high_max - low_min)) * 100
        return stochastic

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, num_std_dev=2):
        sma = prices.rolling(window=period).mean()
        rstd = prices.rolling(window=period).std()
        upper_band = sma + rstd * num_std_dev
        lower_band = sma - rstd * num_std_dev
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_directional_indicators(high_prices, low_prices, close_prices, period):
        positive_movement = [max(0, high_prices.iloc[i] - high_prices.iloc[i - 1]) for i in range(1, len(high_prices))]
        negative_movement = [max(0, low_prices.iloc[i - 1] - low_prices.iloc[i]) for i in range(1, len(low_prices))]
        tr = [max(high_prices.iloc[i] - low_prices.iloc[i], abs(high_prices.iloc[i] - close_prices.iloc[i - 1]), abs(low_prices.iloc[i] - close_prices.iloc[i - 1])) for i in range(1, len(close_prices))]
        tr_smoothed = pd.Series(tr).rolling(window=period).sum()
        pdi = 100 * pd.Series(positive_movement).rolling(window=period).sum() / tr_smoothed
        ndi = 100 * pd.Series(negative_movement).rolling(window=period).sum() / tr_smoothed
        return pdi, ndi

    @staticmethod
    def calculate_adx(high_prices, low_prices, close_prices, period=14):
        pdi, ndi = Indicator.calculate_directional_indicators(high_prices, low_prices, close_prices, period)
        adx_series = (abs(pdi - ndi) / (pdi + ndi)).replace([np.inf, -np.inf], np.nan).dropna().rolling(window=period).mean() * 100
        return adx_series
