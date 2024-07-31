import time
import asyncio
import logging
from threading import Thread
from automacao.models import TradingDecision
from django.utils import timezone
from services.decision_service import DecisionService
from services.currency_pair_service import CurrencyPairService
from services.chart_data_service import ChartDataService

class RoboService:
    def __init__(self, decision_service=None, currency_pair_service=None, learning_service=None, api_service=None):
        self.decision_service = decision_service or DecisionService()
        self.currency_pair_service = currency_pair_service or CurrencyPairService(ChartDataService())
        self.learning_service = learning_service
        self.api_service = api_service
        self.last_decisions = {}
        self.running = True
        self.observer_thread = Thread(target=self.run_observer, daemon=True)
        self.observer_thread.start()

    def run_observer(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self.running:
            try:
                loop.run_until_complete(self.check_and_update_decisions())
            except Exception as e:
                logging.error(f"Erro durante a observação: {e}")
            time.sleep(300)

    async def check_and_update_decisions(self):
        currency_pairs = self.currency_pair_service.get_currency_pairs()
        for pair in currency_pairs:
            await self.process_pair(pair)

    async def process_pair(self, pair):
        try:
            prices = await self.fetch_price_data(pair)
            if self.are_prices_sufficient(prices):
                await self.evaluate_and_update_decision(pair, prices)
        except Exception as e:
            logging.error(f"Erro ao processar {pair}: {e}")

    async def fetch_price_data(self, pair):
        return (
            await self.currency_pair_service.fetch_price_data(pair, "5m"),
            await self.currency_pair_service.fetch_price_data(pair, "15m"),
            await self.currency_pair_service.fetch_price_data(pair, "1h")
        )

    def are_prices_sufficient(self, prices):
        return all(len(price) >= 14 for price in prices)

    async def evaluate_and_update_decision(self, pair, prices):
        decision, indicators = await self.decision_service.make_decision(pair, *prices)
        if self.last_decisions.get(pair) != decision:
            logging.info(f"Decisão alterada para {pair}: {decision}")
            self.last_decisions[pair] = decision
            await self.save_decision(pair, decision, indicators)

    async def save_decision(self, currency_pair, decision, indicators):
        TradingDecision.objects.create(currency_pair=currency_pair, decision=decision)
        success = decision in ["Compra", "Venda"]
        await self.learning_service.store_result(indicators, success)

    def stop_observer(self):
        self.running = False
        if self.observer_thread.is_alive():
            self.observer_thread.join()

# Função principal para iniciar o serviço
def main():
    robo_service = RoboService()
    robo_service.run_observer()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
