import requests
import logging  # Ainda é necessário importar para usar logging.error()

class ChartDataService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.alphavantage.co/query'

    def fetch_time_series_intraday(self, symbol, interval):
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {e}")
            raise
