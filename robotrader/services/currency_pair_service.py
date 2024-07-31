import logging
import asyncio
import requests
import pandas as pd
from services.decision_service import DecisionService
from services.chart_data_service import ChartDataService

class CurrencyPairService:
    def __init__(self, chart_data_service=None):
        self.chart_data_service = chart_data_service or ChartDataService()
        self.currency_pairs = self.chart_data_service.get_available_symbols()
        self.min_data_points = 100
        self.base_url = "https://api.binance.com/api/v3/klines"

    def get_currency_pairs(self):
        return self.currency_pairs

    async def get_realtime_data(self, symbol):
        try:
            async for data in self.chart_data_service.get_realtime_data(symbol):
                yield data
        except Exception as e:
            self._log_error(f"Erro ao obter dados em tempo real para {symbol}: {e}")
            raise

    async def fetch_price_data(self, symbol, interval):
        try:
            params = {'symbol': symbol, 'interval': interval, 'limit': 100}
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if not data or 'code' in data:
                raise ValueError(f"Erro ao buscar dados históricos para {symbol} com intervalo {interval}")

            df = pd.DataFrame(data, columns=[
                'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Close Time', 'Quote Asset Volume', 'Number of Trades',
                'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
            ])
            df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
            df.set_index('Open Time', inplace=True)
            return df
        except Exception as e:
            logging.error(f"Erro ao buscar dados históricos para {symbol} com intervalo {interval}: {e}")
            raise

    async def analyze_currency_pair(self, symbol):
        decision_service = DecisionService()
        try:
            async for data in self.get_realtime_data(symbol):
                decision, indicators = await decision_service.make_decision(
                    symbol, data)
                print({'symbol': symbol, 'decision': decision, 'indicators': indicators})
        except ValueError as e:
            self._log_error(f"Erro na análise do par de moedas {symbol}: {e}")

    @staticmethod
    def _log_error(message):
        logging.error(message)

async def main():
    currency_service = CurrencyPairService()
    available_symbols = currency_service.get_currency_pairs()
    print("Available symbols:", available_symbols)
    tasks = [currency_service.analyze_currency_pair(symbol) for symbol in available_symbols]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
