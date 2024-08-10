import pandas as pd
import numpy as np
import logging
from .indicator_service import Indicator, PriceDataError

class PriceDataError(Exception):
    """Exceção personalizada para erros relacionados a dados de preços."""
    def __init__(self, message):
        super().__init__(message)

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
    def validate_and_convert(series):
        if not isinstance(series, pd.Series):
            raise PriceDataError("A entrada deve ser uma série do pandas.")
        try:
            series = pd.to_numeric(series)
        except ValueError:
            raise PriceDataError("Falha ao converter série para numérico.")
        return series

    @staticmethod
    def log_and_raise_error(message):
        logging.error(message)
        raise PriceDataError(message)

    @staticmethod
    def calculate_combined_stochastic_rsi(high_prices, low_prices, close_prices, rsi_period=7, stochastic_period=14):
        try:
            UtilService.validate_series(close_prices, "Preços de fechamento", max(rsi_period, stochastic_period))
            rsi = Indicator.calculate_rsi(close_prices, rsi_period).iloc[-1]
            stochastic = Indicator.calculate_stochastic_oscillator(high_prices, low_prices, close_prices, stochastic_period).iloc[-1]
            return rsi, stochastic
        except PriceDataError as e:
            logging.error(f"Erro ao calcular Stochastic RSI: {e}")
            return None, None

    @staticmethod
    def get_ema_direction_and_touches(prices, period=9, threshold=0.03):
        try:
            UtilService.validate_series(prices, "EMA Direction and Touches", period)
            ema = Indicator.calculate_ema(prices, period)
            direction = "up" if ema.iloc[-1] > ema.iloc[-2] else "down"
            ema_touches = UtilService.calculate_ema_touches(prices, ema, threshold)
            return direction, ema_touches
        except PriceDataError as e:
            logging.error(f"Erro ao calcular direção e toques da EMA: {e}")
            return None, 0

    @staticmethod
    def calculate_ema_touches(prices, ema, threshold=0.03):
        ema_touches = 0
        touch_flag = False
        try:
            for i in range(1, len(prices)):
                price_distance = abs(prices.iloc[i] - ema.iloc[i]) / ema.iloc[i]
                if price_distance <= threshold and not touch_flag:
                    touch_flag = True
                elif touch_flag and ((prices.iloc[i] > ema.iloc[i] and prices.iloc[i-1] < ema.iloc[i-1]) or 
                                     (prices.iloc[i] < ema.iloc[i] and prices.iloc[i-1] > ema.iloc[i-1])):
                    ema_touches += 1
                    touch_flag = False
        except Exception as e:
            logging.error(f"Erro ao calcular toques da EMA: {e}")
        return ema_touches

    @staticmethod
    def calculate_price_change(prices):
        try:
            if prices.empty or prices.iloc[0] == 0:
                UtilService.log_and_raise_error("Preço inicial não pode ser zero para calcular a mudança de preço.")
            price_change = ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100
            return price_change
        except Exception as e:
            logging.error(f"Erro ao calcular mudança de preço: {e}")
            return None

    @staticmethod
    def identify_patterns(prices):
        try:
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
        except Exception as e:
            logging.error(f"Erro ao identificar padrões: {e}")
            return {'topo_duplo': [], 'fundo_duplo': []}

    @staticmethod
    def is_double_top(segment):
        return segment.iloc[1] == max(segment[:3]) and segment.iloc[3] == max(segment[2:])

    @staticmethod
    def is_double_bottom(segment):
        return segment.iloc[1] == min(segment[:3]) and segment.iloc[3] == min(segment[2:])

    @staticmethod
    def calculate_support_and_resistance(prices):
        try:
            if len(prices) < 2:
                logging.warning("Dados insuficientes para calcular suporte e resistência.")
                return {'support': None, 'resistance': None}
            high = prices.max()
            low = prices.min()
            pivot_point = (high + low + prices.iloc[-1]) / 3
            support = 2 * pivot_point - high
            resistance = 2 * pivot_point - low
            return {'support': support, 'resistance': resistance}
        except Exception as e:
            logging.error(f"Erro ao calcular suporte e resistência: {e}")
            return {'support': None, 'resistance': None}

    @staticmethod
    def calculate_directional_movement(high_prices, low_prices):
        try:
            positive_movement = [max(0, high_prices.iloc[i] - high_prices.iloc[i - 1]) for i in range(1, len(high_prices))]
            negative_movement = [max(0, low_prices.iloc[i - 1] - low_prices.iloc[i]) for i in range(1, len(low_prices))]
            return positive_movement, negative_movement
        except Exception as e:
            logging.error(f"Erro ao calcular movimento direcional: {e}")
            return [], []

    @staticmethod
    def check_ema_50_breakout_and_flow(prices):
        """
        Verifica se a vela rompeu a EMA de 50 e se, nas duas últimas vezes em que houve rompimento, 
        a vela seguiu o fluxo de rompimento sem retração. Se sim, a terceira vez provavelmente seguirá o padrão.
        """
        try:
            UtilService.validate_series(prices, "EMA 50", 50)
            ema_50 = Indicator.calculate_ema(prices, 50)
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
        except PriceDataError as e:
            logging.error(f"Erro ao verificar rompimento da EMA 50: {e}")
            return False
