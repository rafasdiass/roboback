import pandas as pd
import numpy as np
import logging
from indicator_service import Indicator, PriceDataError

class UtilService:
    @staticmethod
    def validate_series(series, name, min_length):
        if not isinstance(series, pd.Series):
            raise PriceDataError(f"{name} deve ser uma série de números.")
        if len(series) < min_length:
            raise PriceDataError(f"Não há dados suficientes para calcular o indicador {name}. Esperado: {min_length}, fornecido: {len(series)}")
        if series.isnull().any():
            raise PriceDataError(f"{name} contém valores nulos.")
        if not np.isfinite(series).all():
            raise PriceDataError(f"{name} contém valores infinitos.")

    @staticmethod
    def log_and_raise_error(message):
        logging.error(message)
        raise PriceDataError(message)

    @staticmethod
    def calculate_combined_stochastic_rsi(high_prices, low_prices, close_prices, rsi_period=7, stochastic_period=14):
        UtilService.validate_series(close_prices, "Preços de fechamento", max(rsi_period, stochastic_period))
        rsi = Indicator.calculate_rsi(close_prices, rsi_period).iloc[-1]
        stochastic = Indicator.calculate_stochastic_oscillator(high_prices, low_prices, close_prices, stochastic_period).iloc[-1]
        return rsi, stochastic

    @staticmethod
    def get_ema_direction_and_touches(prices, period=9, threshold=0.03):
        UtilService.validate_series(prices, "EMA Direction and Touches", period)
        ema = Indicator.calculate_ema(prices, period)
        direction = "up" if ema.iloc[-1] > ema.iloc[-2] else "down"
        ema_touches = UtilService.calculate_ema_touches(prices, ema, threshold)
        return direction, ema_touches

    @staticmethod
    def calculate_ema_touches(prices, ema, threshold=0.03):
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
    def calculate_price_change(prices):
        if prices.empty or prices.iloc[0] == 0:
            UtilService.log_and_raise_error("Preço inicial não pode ser zero para calcular a mudança de preço.")
        price_change = ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100
        return price_change

    @staticmethod
    def identify_patterns(prices):
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
    def calculate_support_and_resistance(prices):
        if len(prices) < 2:
            logging.warning("Dados insuficientes para calcular suporte e resistência.")
            return {'support': None, 'resistance': None}
        high = prices.max()
        low = prices.min()
        pivot_point = (high + low + prices.iloc[-1]) / 3
        support = 2 * pivot_point - high
        resistance = 2 * pivot_point - low
        return {'support': support, 'resistance': resistance}

    @staticmethod
    def calculate_directional_movement(high_prices, low_prices):
        positive_movement = [max(0, high_prices.iloc[i] - high_prices.iloc[i - 1]) for i in range(1, len(high_prices))]
        negative_movement = [max(0, low_prices.iloc[i - 1] - low_prices.iloc[i]) for i in range(1, len(low_prices))]
        return positive_movement, negative_movement

    @staticmethod
    def check_ema_50_breakout_and_flow(prices):
        """
        Verifica se a vela rompeu a EMA de 50 e se, nas duas últimas vezes em que houve rompimento, 
        a vela seguiu o fluxo de rompimento sem retração. Se sim, a terceira vez provavelmente seguirá o padrão.
        """
        UtilService.validate_series(prices, "EMA 50", 50)
        ema_50 = Indicator.calculate_ema_50(prices)
        latest_price = prices.iloc[-1]

        # Verifica se a última vela rompeu a EMA de 50
        if latest_price > ema_50.iloc[-1] and prices.iloc[-2] <= ema_50.iloc[-2]:
            successful_breakouts = 0
            
            # Procura pelas duas últimas vezes que houve rompimento
            for i in range(-3, -len(prices), -1):
                if prices.iloc[i] > ema_50.iloc[i] and prices.iloc[i-1] <= ema_50.iloc[i-1]:
                    # Verifica se houve continuidade do fluxo nas velas seguintes
                    if prices.iloc[i+1] > ema_50.iloc[i+1] and prices.iloc[i+2] > ema_50.iloc[i+2]:
                        successful_breakouts += 1
                    if successful_breakouts == 2:
                        return True  # Nas duas últimas vezes o fluxo continuou, então provavelmente continuará novamente
            
        return False  # Não houve rompimento recente, ou nas últimas duas vezes o fluxo não continuou
