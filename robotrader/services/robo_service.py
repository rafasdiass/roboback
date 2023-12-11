import time
from threading import Thread
from automacao.models import TradingDecision
from django.utils import timezone

class RoboService:
    def __init__(self, decision_service, currency_pair_service, learning_service, api_service):
        self.decision_service = decision_service
        self.currency_pair_service = currency_pair_service
        self.learning_service = learning_service
        self.api_service = api_service
        self.last_decisions = {}
        self.running = True
        self.observer_thread = Thread(target=self.run_observer, daemon=True)
        self.observer_thread.start()

    def run_observer(self):
        while self.running:
            try:
                self.check_and_update_decisions()
            except Exception as e:
                print(f"Erro durante a observação: {e}")
            time.sleep(300)  # Espera por 5 minutos

    def check_and_update_decisions(self):
        currency_pairs = self.currency_pair_service.get_currency_pairs()
        for pair in currency_pairs:
            self.process_pair(pair)

    def process_pair(self, pair):
        try:
            prices5min, prices15min, prices1h = self.fetch_price_data(pair)
            if self.are_prices_sufficient(prices5min, prices15min, prices1h):
                self.evaluate_and_update_decision(pair, prices5min, prices15min, prices1h)
        except Exception as e:
            print(f"Erro ao processar {pair}: {e}")

    def fetch_price_data(self, pair):
        return (
            self.currency_pair_service.fetch_price_data(pair, "5min"),
            self.currency_pair_service.fetch_price_data(pair, "15min"),
            self.currency_pair_service.fetch_price_data(pair, "1h")
        )

    def are_prices_sufficient(self, prices5min, prices15min, prices1h):
        return all(len(prices) >= 14 for prices in [prices5min, prices15min, prices1h])

    def evaluate_and_update_decision(self, pair, prices5min, prices15min, prices1h):
        decision, indicators = self.decision_service.make_decision(pair, prices5min, prices15min, prices1h)
        if self.last_decisions.get(pair) != decision:
            print(f"Decisão alterada para {pair}: {decision}")
            self.last_decisions[pair] = decision
            self.save_decision(pair, decision, indicators)

    def save_decision(self, currency_pair, decision, indicators):
        TradingDecision.objects.create(currency_pair=currency_pair, decision=decision)
        success = decision in ["Compra", "Venda"]
        self.learning_service.store_result(indicators, success)

    def stop_observer(self):
        self.running = False
        if self.observer_thread.is_alive():
            self.observer_thread.join()
