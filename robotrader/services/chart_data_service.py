import yfinance as yf
import logging

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
            data = yf.download(forex_symbol, period="5d", interval=interval_map[interval])
            return data.to_dict('records')  # Convertendo para um formato serializável
        except Exception as e:
            logging.error(f"Erro ao buscar dados: {e}")
            raise
