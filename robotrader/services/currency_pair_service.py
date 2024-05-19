import logging
import asyncio
from .chart_data_service import ChartDataService
from .decision_service import DecisionService
import pandas as pd

class CurrencyPairService:
    def __init__(self, chart_data_service=None):
        self.chart_data_service = chart_data_service or ChartDataService()
        self.currency_pairs = ['EURUSD', 'AUDCAD']
        self.min_data_points = 100
        self.last_call = asyncio.get_event_loop().time()

    def get_currency_pairs(self):
        """ Retorna a lista de pares de moedas disponíveis. """
        return self.currency_pairs

    async def fetch_price_data(self, symbol, interval):
        """ Obtém dados de preços para um par de moedas específico e intervalo de tempo. """
        try:
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - self.last_call
            if elapsed < 72:
                await asyncio.sleep(72 - elapsed)
            self.last_call = asyncio.get_event_loop().time()
            data = await self.chart_data_service.fetch_real_time_data(symbol)
            return self._validate_and_return_data(data, symbol, interval)
        except Exception as e:
            self._log_error(f"Erro ao obter dados para {symbol} no intervalo {interval}: {e}")
            raise

    def _validate_and_return_data(self, data, symbol, interval):
        if not data or len(data) < self.min_data_points:
            error_message = f"Dados insuficientes para {symbol} no intervalo {interval}."
            self._log_error(error_message)
            raise ValueError(error_message)
        if self._has_significant_gaps(data):
            error_message = f"Lacunas significativas encontradas nos dados de {symbol}."
            self._log_error(error_message)
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

    @staticmethod
    def _log_error(message):
        """ Loga uma mensagem de erro. """
        logging.error(message)

    async def analyze_currency_pair(self, symbol, intervals):
        """ Analisa um par de moedas em diferentes intervalos de tempo. """
        decision_service = DecisionService()
        results = {}
        # Obtenha os dados uma vez para o maior intervalo
        data = await self.fetch_price_data(symbol, max(intervals))
        for interval in intervals:
            try:
                # Interpola os dados para o intervalo atual
                interval_data = self._interpolate_data(data, interval)
                decision, indicators = await decision_service.make_decision(
                    symbol, interval_data['Close'].tolist(), interval_data['High'].tolist(), interval_data['Low'].tolist())
                results[interval] = {'decision': decision, 'indicators': indicators}
            except ValueError as e:
                self._log_error(f"Erro na análise do par de moedas {symbol} no intervalo {interval}: {e}")
        return results

    def _interpolate_data(self, data, interval):
        """ Interpola os dados para o intervalo atual. """
        # Aplica a EMA para suavizar os dados
        smoothed_data = data.ewm(span=9, adjust=False).mean()
        # Interpola os dados suavizados
        interval_data = smoothed_data.resample(f'{interval}T').interpolate(method='time')
        if self._has_significant_gaps(interval_data):
            raise ValueError(f"Lacunas significativas encontradas nos dados interpolados.")
        return interval_data
