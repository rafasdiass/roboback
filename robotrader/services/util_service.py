import pandas as pd
import numpy as np
import logging

class PriceDataError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UtilService:
    @staticmethod
    def validate_prices(prices, period):
        """
        Valida se há dados suficientes para calcular o indicador e se os dados são válidos.
        """
        if not isinstance(prices, list) or not all(isinstance(price, (int, float)) for price in prices):
            raise PriceDataError("Preços devem ser uma lista de números.")

        if len(prices) < period:
            raise PriceDataError(f"Não há dados suficientes para calcular o indicador. Esperado: {period}, fornecido: {len(prices)}")

    @staticmethod
    def calculate_rsi(prices, period=7):
        """
        Calcula o Índice de Força Relativa (RSI).
        """
        UtilService.validate_prices(prices, period + 1)

        prices_series = pd.Series(prices)
        delta = prices_series.diff().dropna()
        up, down = delta.clip(lower=0), -delta.clip(upper=0)

        roll_up = up.ewm(span=period).mean()
        roll_down = down.ewm(span=period).mean()

        RS = roll_up / roll_down
        return 100.0 - (100.0 / (1.0 + RS))

    @staticmethod
    def calculate_stochastic_oscillator(high_prices, low_prices, close_prices, period=14):
        """
        Calcula o Oscilador Estocástico.
        """
        UtilService.validate_prices(high_prices, period)
        UtilService.validate_prices(low_prices, period)
        UtilService.validate_prices(close_prices, period)

        high_max = pd.Series(high_prices).rolling(window=period).max()
        low_min = pd.Series(low_prices).rolling(window=period).min()

        return ((close_prices[-1] - low_min[-1]) / (high_max[-1] - low_min[-1])) * 100

    @staticmethod
    def calculate_combined_stochastic_rsi(high_prices, low_prices, close_prices, rsi_period=7, stochastic_period=14):
        """
        Calcula uma combinação de Stochastic RSI.
        """
        max_period = max(rsi_period, stochastic_period)
        UtilService.validate_prices(close_prices, max_period)

        rsi = UtilService.calculate_rsi(close_prices, rsi_period)
        stochastic = UtilService.calculate_stochastic_oscillator(high_prices, low_prices, close_prices, stochastic_period)

        return rsi, stochastic

    @staticmethod
    def calculate_ema(prices, period=9):
        """
        Calcula a Média Móvel Exponencial (EMA).
        """
        UtilService.validate_prices(prices, period)

        prices_series = pd.Series(prices)
        return prices_series.ewm(span=period, adjust=False).mean().iloc[-1]

    @staticmethod
    def get_ema_direction_and_touches(prices, period=9):
        """
        Determina a direção da EMA e conta o número de toques.
        """
        UtilService.validate_prices(prices, period)

        prices_series = pd.Series(prices)
        ema = prices_series.ewm(span=period, adjust=False).mean()
        direction = "up" if ema.iloc[-1] > ema.iloc[-2] else "down"

        return direction, UtilService.calculate_ema_touches(prices_series, ema)

    @staticmethod
    def calculate_ema_touches(prices_series, ema_series, threshold=0.03):
        """
        Calcula o número de toques na EMA.
        """
        ema_touches = 0
        touch_flag = False

        for i in range(1, len(prices_series)):
            price_distance = abs(prices_series[i] - ema_series[i]) / ema_series[i]

            if price_distance <= threshold and not touch_flag:
                touch_flag = True
            elif touch_flag and ((prices_series[i] > ema_series[i] and prices_series[i-1] < ema_series[i-1]) or \
                                 (prices_series[i] < ema_series[i] and prices_series[i-1] > ema_series[i-1])):
                ema_touches += 1
                touch_flag = False

        return ema_touches

    @staticmethod
    def calculate_price_change(prices):
        """
        Calcula a mudança percentual do preço.
        """
        if not prices or prices[0] == 0:
            raise PriceDataError("Preço inicial não pode ser zero para calcular a mudança de preço.")

        try:
            return ((prices[-1] - prices[0]) / prices[0]) * 100
        except Exception as e:
            logging.error(f"Erro ao calcular a mudança de preço: {e}")
            raise

    @staticmethod
    def identify_patterns(prices):
        """
        Identifica padrões comuns como topo duplo e fundo duplo.
        """
        if len(prices) < 5:
            logging.warning("Dados insuficientes para identificar padrões.")
            return {'topo_duplo': [], 'fundo_duplo': []}

        topo_duplo, fundo_duplo = [], []

        for i in range(4, len(prices)):
            segment = prices[i-4:i+1]
            if UtilService.is_double_top(segment):
                topo_duplo.append(i-2)
            if UtilService.is_double_bottom(segment):
                fundo_duplo.append(i-2)

        return {'topo_duplo': topo_duplo, 'fundo_duplo': fundo_duplo}

    @staticmethod
    def is_double_top(segment):
        """
        Verifica se um segmento de preços forma um topo duplo.
        """
        return segment[1] == max(segment[:3]) and segment[3] == max(segment[2:])

    @staticmethod
    def is_double_bottom(segment):
        """
        Verifica se um segmento de preços forma um fundo duplo.
        """
        return segment[1] == min(segment[:3]) and segment[3] == min(segment[2:])

    @staticmethod
    def calculate_support_and_resistance(prices):
        """
        Calcula níveis de suporte e resistência.
        """
        if len(prices) < 2:
            logging.warning("Dados insuficientes para calcular suporte e resistência.")
            return {'support': None, 'resistance': None}

        high = max(prices)
        low = min(prices)
        pivot_point = (high + low + prices[-1]) / 3

        return {'support': 2 * pivot_point - high, 'resistance': 2 * pivot_point - low}

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, num_std_dev=2):
        """
        Calcula as Bandas de Bollinger.
        """
        UtilService.validate_prices(prices, period)

        prices_series = pd.Series(prices)
        sma = prices_series.rolling(window=period).mean()
        rstd = prices_series.rolling(window=period).std()

        upper_band = sma + rstd * num_std_dev
        lower_band = sma - rstd * num_std_dev

        return upper_band, sma, lower_band

    # Métodos para calcular o ADX e os Indicadores Direcionais
    @staticmethod
    def calculate_directional_movement(high_prices, low_prices):
        """
        Calcula os movimentos direcionais positivo e negativo.
        """
        positive_movement = [max(0, high_prices[i] - high_prices[i - 1]) for i in range(1, len(high_prices))]
        negative_movement = [max(0, low_prices[i - 1] - low_prices[i]) for i in range(1, len(low_prices))]

        return positive_movement, negative_movement

    @staticmethod
    def calculate_directional_indicators(high_prices, low_prices, close_prices, period):
        """
        Calcula os indicadores direcionais (+DI e -DI).
        """
        positive_movement, negative_movement = UtilService.calculate_directional_movement(high_prices, low_prices)

        tr = [max(high_prices[i] - low_prices[i], abs(high_prices[i] - close_prices[i - 1]), abs(low_prices[i] - close_prices[i - 1])) for i in range(1, len(close_prices))]
        tr_smoothed = pd.Series(tr).rolling(window=period).sum()

        pdi = 100 * pd.Series(positive_movement).rolling(window=period).sum() / tr_smoothed
        ndi = 100 * pd.Series(negative_movement).rolling(window=period).sum() / tr_smoothed

        return pdi, ndi

    @staticmethod
    def calculate_adx(high_prices, low_prices, close_prices, period=14):
        """
        Calcula o Índice Direcional Médio (ADX).
        """
        UtilService.validate_prices(close_prices, period + 1)

        pdi, ndi = UtilService.calculate_directional_indicators(high_prices, low_prices, close_prices, period)
        adx_series = (abs(pdi - ndi) / (pdi + ndi)).replace([np.inf, -np.inf], 0).fillna(0) * 100
        adx = adx_series.ewm(span=period, adjust=False).mean()

        return adx.iloc[-1]
