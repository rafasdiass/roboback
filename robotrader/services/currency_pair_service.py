from .chart_data_service import ChartDataService

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
        if not self.chart_data_service:
            raise ValueError("ChartDataService não está definido.")

        data = self.chart_data_service.fetch_time_series_intraday(symbol, interval)

        if not self.validate_data(data):
            raise ValueError(f"Dados insuficientes ou inconsistentes para {symbol} no intervalo {interval}.")

        return data

    def validate_data(self, data):
        """
        Valida a integridade e completude dos dados de preços.
        """
        if data is None or len(data) < self.min_data_points:
            return False  # Dados insuficientes para análise.

        # Verificar lacunas significativas nos dados
        if self.has_significant_gaps(data):
            return False  # Lacunas significativas encontradas.

        return True  # Dados validados com sucesso.

    def has_significant_gaps(self, data):
        """
        Verifica se há lacunas significativas nos dados.
        """
        # Implementação simplificada. Adapte conforme necessário.
        max_allowed_gap = 2  # Define o tamanho máximo permitido para uma lacuna.
        for i in range(1, len(data)):
            if data.index[i] - data.index[i - 1] > max_allowed_gap:
                return True  # Lacuna significativa encontrada.
        
        return False  # Nenhuma lacuna significativa encontrada.

# Exemplo de uso:
# service = CurrencyPairService()
# data = service.fetch_price_data('EURUSD', '1h')
