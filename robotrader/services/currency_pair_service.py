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
        self.decision_service = DecisionService()  # Inicializando o DecisionService aqui

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
            df, source = await self.chart_data_service.fetch_intraday_data(symbol, interval)
            return df
        except Exception as e:
            logging.error(f"Erro ao buscar dados históricos para {symbol} com intervalo {interval}: {e}")
            raise

    async def analyze_currency_pair(self, symbol):
        try:
            async for data in self.get_realtime_data(symbol):
                decision, indicators = await self.decision_service.make_decision(symbol, data)
                print({'symbol': symbol, 'decision': decision, 'indicators': indicators})
        except ValueError as e:
            self._log_error(f"Erro na análise do par de moedas {symbol}: {e}")

    @staticmethod
    def _log_error(message):
        logging.error(message)
