import yfinance as yf
import logging
import pandas as pd

class ChartDataService:
    def fetch_time_series_intraday(self, symbol, interval):
        interval_map = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "1h": "1h"
        }
        forex_symbol = f"{symbol}=X"
        try:
            # Considerar aumentar o período se necessário
            data = yf.download(forex_symbol, period="3mo", interval=interval_map[interval])
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            return data
        except Exception as e:
            logging.error(f"Erro ao buscar dados para {forex_symbol}: {e}")
            raise
