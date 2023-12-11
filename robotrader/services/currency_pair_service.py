from .chart_data_service import ChartDataService

class CurrencyPairService:
    def __init__(self, chart_data_service=None):
        self.chart_data_service = chart_data_service or ChartDataService()
        self.currency_pairs = ['EURUSD', 'AUDCAD']

    def get_currency_pairs(self):
        return self.currency_pairs

    def fetch_price_data(self, symbol, interval):
        return self.chart_data_service.fetch_time_series_intraday(symbol, interval)
