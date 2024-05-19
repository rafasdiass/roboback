import logging
from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

class ChartDataService:
    def __init__(self, api_key=api_key):
        self.fx = ForeignExchange(key=api_key)

    async def fetch_real_time_data(self, symbol):
        forex_symbol = f"{symbol}"
        try:
            data, _ = await self.fx.get_currency_exchange_intraday(forex_symbol, 'USD', interval='1min', outputsize='full')
            return self._format_data(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados para {forex_symbol}: {e}")
            raise

    @staticmethod
    def _format_data(data):
        data_frame = pd.DataFrame.from_dict(data).T
        data_frame.index = pd.to_datetime(data_frame.index)
        return data_frame
