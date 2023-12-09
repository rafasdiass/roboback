from .chart_data_service import ChartDataService

class CurrencyPairService:
    def __init__(self, chart_data_service):
        self.chart_data_service = chart_data_service
        self.currency_pairs = ['EURUSD', 'AUDCAD']

    def get_currency_pairs(self):
        # Retorna a lista de pares de moeda disponíveis para análise
        return self.currency_pairs

    def fetch_price_data(self, symbol, interval):
        # Utiliza o ChartDataService para buscar os dados de preço
        return self.chart_data_service.fetch_time_series_intraday(symbol, interval)
