# services/currency_pair_service.py

class CurrencyPairService:
    def __init__(self, api_service):
        self.api_service = api_service
        self.currency_pairs = ['EURUSD', 'AUDCAD']
        self.closing_prices = {
            '5min': [],
            '15min': [],
            '1h': []
        }

    def calculate_fibonacci_levels(self, low, high):
        fibo_levels = [0.382, 0.5, 0.618]
        return [low + (high - low) * level for level in fibo_levels]

    def fetch_price_data(self, symbol, interval):
        # Aqui você pode chamar seu ApiService para buscar dados
        # Por simplicidade, estou omitindo a chamada real e a lógica de tratamento de resposta
        # Você precisará implementar a lógica de chamada da API e processamento da resposta
        pass

    def process_price_data_response(self, response, interval):
        # Processar a resposta da API e extrair os preços de fechamento
        # Esta é uma adaptação simplificada
        key = f"Time Series ({interval})"
        if key in response:
            time_series = response[key]
            closing_prices = [float(entry['4. close']) for entry in time_series.values()]
            self.update_closing_prices(interval, closing_prices)

    def update_closing_prices(self, interval, closing_prices):
        self.closing_prices[interval] = closing_prices
