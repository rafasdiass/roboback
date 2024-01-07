import logging
from throttler import Throttler
from .chart_data_service import ChartDataService
from .decision_service import DecisionService
import pandas as pd

class CurrencyPairService:
    def __init__(self, chart_data_service=None):
        self.chart_data_service = chart_data_service or ChartDataService()
        self.currency_pairs = ['EURUSD', 'AUDCAD']
        self.min_data_points = 100
        self.rate_limiter = Throttler(rate_limit=10, period=1)  # Supondo 10 chamadas por segundo

    def get_currency_pairs(self):
        """ Retorna a lista de pares de moedas disponíveis. """
        return self.currency_pairs

    async def fetch_price_data(self, symbol, interval):
        """ Obtém dados de preços para um par de moedas específico e intervalo de tempo. """
        try:
            async with self.rate_limiter:
                data = await self.chart_data_service.fetch_real_time_data(symbol)
            return self._validate_and_return_data(data, symbol, interval)
        except Exception as e:
            logging.error(f"Erro ao obter dados para {symbol} no intervalo {interval}: {e}")
            raise

    def _validate_and_return_data(self, data, symbol, interval):
        if not data or len(data) < self.min_data_points:
            error_message = f"Dados insuficientes para {symbol} no intervalo {interval}."
            logging.error(error_message)
            raise ValueError(error_message)
        if self._has_significant_gaps(data):
            error_message = f"Lacunas significativas encontradas nos dados de {symbol}."
            logging.error(error_message)
            raise ValueError(error_message)
        return data

    def _has_significant_gaps(self, data):
        """ Verifica se há lacunas significativas nos dados. """
        self._validate_dataframe(data)
        max_allowed_gap = pd.Timedelta(days=2)
        return any(data.index[i] - data.index[i - 1] > max_allowed_gap for i in range(1, len(data)))

    @staticmethod
    def _validate_dataframe(data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Os dados devem ser um DataFrame do pandas.")

    async def analyze_currency_pair(self, symbol, intervals):
        """ Analisa um par de moedas em diferentes intervalos de tempo. """
        decision_service = DecisionService()
        results = {}
        for interval in intervals:
            try:
                data = await self.fetch_price_data(symbol, interval)
                decision, indicators = await decision_service.make_decision(
                    symbol, data['Close'].tolist(), data['High'].tolist(), data['Low'].tolist())
                results[interval] = {'decision': decision, 'indicators': indicators}
            except ValueError as e:
                logging.error(f"Erro na análise do par de moedas {symbol} no intervalo {interval}: {e}")
        return results
