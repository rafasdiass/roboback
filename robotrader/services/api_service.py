import requests
import logging

class RoboDecision:
    def __init__(self, currencyPair, decision, time):
        self.currencyPair = currencyPair
        self.decision = decision
        self.time = time

class APIService:
    def __init__(self, api_key):
        self.api_key = api_key
        # URL base para a API da Alpha Vantage
        self.base_url = 'https://www.alphavantage.co/query'
        # URL para buscar decisões do robô do seu backend
        self.decisions_url = 'http://127.0.0.1:8080/api/robo-decisions'

    def fetch_time_series_intraday(self, symbol, interval):
        # Constrói os parâmetros da requisição
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key
        }
        try:
            # Faz a requisição à API da Alpha Vantage
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {e}")
            raise

    def fetch_robo_decisions(self):
        try:
            # Faz a requisição ao seu backend para obter as decisões do robô
            response = requests.get(self.decisions_url, timeout=10)
            if response.status_code == 200:
                decisions_data = response.json()
                decisions = [RoboDecision(**d) for d in decisions_data]
                return decisions
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {e}")
            raise

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Uso do APIService
api_service = APIService(api_key='NB19FGHNM74Q9QAU')

# Exemplo de busca de dados de série temporal intradiária
try:
    data = api_service.fetch_time_series_intraday(symbol='EURUSD', interval='5min')
    print(f"Dados para EURUSD: {data}")
except Exception as err:
    print(f"Erro ao fazer a requisição para EURUSD: {err}")

# Exemplo de busca de decisões do robô
try:
    robo_decisions = api_service.fetch_robo_decisions()
    for decision in robo_decisions:
        print(f"{decision.currencyPair}: {decision.decision} at {decision.time}")
except Exception as err:
    print(f"Erro ao obter decisões do robô: {err}")
