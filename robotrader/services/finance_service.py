# services/finance_service.py

import requests

class FinanceService:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def mount_alpha_vantage_url(self, function_type, symbol, interval):
        return f"{self.base_url}/query?function={function_type}&symbol={symbol}&interval={interval}&apikey={self.api_key}"

    def mount_get_request(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("API Error:", e)
            return None

    def get_stock_data(self, symbol, interval):
        url = self.mount_alpha_vantage_url('TIME_SERIES_INTRADAY', symbol, interval)
        return self.mount_get_request(url)

    def get_figures(self, symbol, interval, series_type):
        function_type = 'SMA'  # Por exemplo, usando Média Móvel Simples
        url = f"{self.base_url}/query?function={function_type}&symbol={symbol}&interval={interval}&time_period=10&series_type={series_type}&apikey={self.api_key}"
        return self.mount_get_request(url)
