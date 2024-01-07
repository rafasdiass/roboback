import PythonMetaTrader5 as mt5
import pandas as pd
import logging

class ChartDataService:
    def __init__(self):
        pass

    def connect(self):
        if not mt5.initialize():
            logging.error("Erro ao conectar ao servidor MetaTrader 5")
            return False
        return True

    def disconnect(self):
        mt5.shutdown()

    def fetch_real_time_data(self, symbol):
        forex_symbol = f"{symbol}"
        try:
            symbol_info = mt5.symbol_info(forex_symbol)
            if symbol_info is None:
                logging.error(f"{forex_symbol} não encontrado, erro {mt5.last_error()}")
                return None

            if not symbol_info.visible:
                logging.error(f"{forex_symbol} não é visível, tentando mudar...")
                if not mt5.symbol_select(forex_symbol, True):
                    logging.error(f"symbol_select({forex_symbol}) falhou, erro {mt5.last_error()}")
                    return None

            ticks = mt5.copy_ticks_from(forex_symbol, mt5.TIME_CURRENT, 1000, mt5.COPY_TICKS_ALL)
            data_frame = pd.DataFrame(ticks)
            data_frame['time'] = pd.to_datetime(data_frame['time'], unit='s')
            return data_frame
        except Exception as e:
            logging.error(f"Erro ao buscar dados para {forex_symbol}: {e}")
            raise
        finally:
            self.disconnect()
