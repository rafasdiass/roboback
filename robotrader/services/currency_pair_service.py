import pandas as pd
import logging
from .chart_data_service import ChartDataService
from .decision_service import DecisionService

class CurrencyPairService:
    def __init__(self, chart_data_service=None):
        self.chart_data_service = chart_data_service or ChartDataService()
        self.currency_pairs = ['EURUSD', 'AUDCAD']
        self.min_data_points = 100  # Número mínimo de pontos de dados para análise

    def get_currency_pairs(self):
        """
        Retorna a lista de pares de moedas disponíveis.
        """
        return self.currency_pairs

    def fetch_price_data(self, symbol, interval):
        """
        Obtém dados de preços para um par de moedas específico e intervalo de tempo.
        """
        try:
            data = self.chart_data_service.fetch_time_series_intraday(symbol, interval)
            if self.validate_data(data):
                return data
            else:
                raise ValueError(f"Dados insuficientes ou inconsistentes para {symbol} no intervalo {interval}.")
        except Exception as e:
            logging.error(f"Erro ao obter dados para {symbol} no intervalo {interval}: {e}")
            raise

    def validate_data(self, data):
        """
        Verifica se os dados recebidos são suficientes e consistentes.
        """
        if data is None or len(data) < self.min_data_points:
            logging.error(f"Quantidade de dados recebida para análise: {len(data) if data is not None else 0}")
            return False  # Dados insuficientes para análise.

        if self.has_significant_gaps(data):
            logging.error("Lacunas significativas encontradas nos dados.")
            return False  # Lacunas significativas encontradas.

        return True  # Dados validados com sucesso.

    def has_significant_gaps(self, data):
        """
        Verifica se há lacunas significativas nos dados.
        Assume que 'data' é um DataFrame do pandas com índices de data e hora.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Os dados devem ser um DataFrame do pandas.")

        max_allowed_gap = pd.Timedelta(days=2)  # Permitir lacunas de até 2 dias
        last_valid_index = None

        for i in range(len(data)):
            if last_valid_index is not None and data.index[i] - last_valid_index > max_allowed_gap:
                return True  # Lacuna significativa encontrada.
            last_valid_index = data.index[i]

        return False  # Nenhuma lacuna significativa encontrada.

    def analyze_currency_pair(self, symbol, intervals):
        """
        Analisa um par de moedas em diferentes intervalos de tempo.
        """
        decision_service = DecisionService()
        results = {}

        for interval in intervals:
            try:
                data = self.fetch_price_data(symbol, interval)
                if not data.empty:
                    decision, indicators = decision_service.make_decision(symbol, data['Close'].tolist(), data['High'].tolist(), data['Low'].tolist())
                    results[interval] = {'decision': decision, 'indicators': indicators}
            except ValueError as e:
                logging.error(f"Erro na análise do par de moedas {symbol} no intervalo {interval}: {e}")

        return results
