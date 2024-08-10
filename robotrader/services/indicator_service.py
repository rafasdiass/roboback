import pandas as pd
import numpy as np

class PriceDataError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Indicator:
    @staticmethod
    def validate_and_convert(series):
        """
        Valida e converte uma série para numérica, assegurando que não haja valores nulos ou infinitos.
        """
        try:
            series = pd.to_numeric(series, errors='raise')
        except ValueError:
            raise PriceDataError("A série contém valores não numéricos.")
        
        if series.isnull().any():
            raise PriceDataError("A série contém valores nulos.")
        
        if not np.isfinite(series).all():
            raise PriceDataError("A série contém valores infinitos.")
        
        return series

    @staticmethod
    def calculate_sma(prices, period):
        """
        Calcula a média móvel simples (SMA).
        """
        prices = Indicator.validate_and_convert(prices)
        return prices.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(prices, period):
        """
        Calcula a média móvel exponencial (EMA).
        """
        prices = Indicator.validate_and_convert(prices)
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(prices, period=7):
        """
        Calcula o Índice de Força Relativa (RSI).
        """
        prices = Indicator.validate_and_convert(prices)
        delta = prices.diff().dropna()
        up, down = delta.clip(lower=0), -delta.clip(upper=0)
        roll_up = up.ewm(span=period, adjust=False).mean()
        roll_down = down.ewm(span=period, adjust=False).mean()
        RS = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + RS))
        return rsi

    @staticmethod
    def calculate_stochastic_oscillator(high_prices, low_prices, close_prices, period=14):
        """
        Calcula o Oscilador Estocástico.
        """
        high_prices = Indicator.validate_and_convert(high_prices)
        low_prices = Indicator.validate_and_convert(low_prices)
        close_prices = Indicator.validate_and_convert(close_prices)
        
        high_max = high_prices.rolling(window=period).max()
        low_min = low_prices.rolling(window=period).min()
        stochastic = ((close_prices - low_min) / (high_max - low_min)) * 100
        return stochastic

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, num_std_dev=2):
        """
        Calcula as Bandas de Bollinger.
        """
        prices = Indicator.validate_and_convert(prices)
        sma = prices.rolling(window=period).mean()
        rstd = prices.rolling(window=period).std()
        upper_band = sma + rstd * num_std_dev
        lower_band = sma - rstd * num_std_dev
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_directional_indicators(high_prices, low_prices, close_prices, period):
        """
        Calcula os indicadores direcionais positivos e negativos.
        """
        high_prices = Indicator.validate_and_convert(high_prices)
        low_prices = Indicator.validate_and_convert(low_prices)
        close_prices = Indicator.validate_and_convert(close_prices)
        
        positive_movement = [max(0, high_prices.iloc[i] - high_prices.iloc[i - 1]) for i in range(1, len(high_prices))]
        negative_movement = [max(0, low_prices.iloc[i - 1] - low_prices.iloc[i]) for i in range(1, len(low_prices))]
        
        tr = [max(high_prices.iloc[i] - low_prices.iloc[i], 
                  abs(high_prices.iloc[i] - close_prices.iloc[i - 1]), 
                  abs(low_prices.iloc[i] - close_prices.iloc[i - 1])) for i in range(1, len(close_prices))]
        
        tr_smoothed = pd.Series(tr).rolling(window=period).sum()
        pdi = 100 * pd.Series(positive_movement).rolling(window=period).sum() / tr_smoothed
        ndi = 100 * pd.Series(negative_movement).rolling(window=period).sum() / tr_smoothed
        return pdi, ndi

    @staticmethod
    def calculate_adx(high_prices, low_prices, close_prices, period=14):
        """
        Calcula o Índice Direcional Médio (ADX).
        """
        pdi, ndi = Indicator.calculate_directional_indicators(high_prices, low_prices, close_prices, period)
        adx_series = (abs(pdi - ndi) / (pdi + ndi)).replace([np.inf, -np.inf], np.nan).dropna().rolling(window=period).mean() * 100
        return adx_series
