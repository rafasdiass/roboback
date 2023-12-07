import requests

class APIService:
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
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

# Uso do APIService
api_service = APIService(api_key='NB19FGHNM74Q9QAU')

# Exemplo de busca de dados de série temporal intradiária para o símbolo 'IBM' com intervalo de '5min'
try:
    data = api_service.fetch_time_series_intraday(symbol='IBM', interval='5min')
    print(data)
except requests.exceptions.HTTPError as err:
    print(f"Erro ao fazer a requisição: {err}")
