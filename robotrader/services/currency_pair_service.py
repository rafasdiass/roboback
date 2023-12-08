# services/currency_pair_service.py

# Importe APIService
from .api_service import APIService

class CurrencyPairService:
    def __init__(self, api_service):
        self.api_service = api_service
        self.currency_pairs = ['EURUSD', 'AUDCAD']

    def get_currency_pairs(self):
        # Retorna a lista de pares de moeda disponíveis para análise
        return self.currency_pairs

    def fetch_price_data(self, symbol, interval):
        # Utiliza o APIService para buscar os dados de preço
        return self.api_service.fetch_time_series_intraday(symbol, interval)

# Exemplo de uso do CurrencyPairService
# Você deve criar uma instância do APIService em outro lugar no seu código
# e passá-la para CurrencyPairService quando criar uma instância desta classe.
# Exemplo (em algum outro lugar no seu código):
# api_service = APIService(api_key='SUA_CHAVE_API')
# currency_pair_service = CurrencyPairService(api_service)

# O trecho a seguir é apenas um exemplo e deve ser colocado onde você realmente usa o serviço:
# try:
#     price_data = currency_pair_service.fetch_price_data('EURUSD', '5min')
#     print(price_data)
# except requests.exceptions.HTTPError as err:
#     print(f"Erro ao buscar dados de preço: {err}")
