import time
from threading import Thread
from automacao.models import TradingDecision
from django.utils import timezone
import logging

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
        """ Continuously monitors and updates trading decisions. """
        while self.running:
            try:
                self.check_and_update_decisions()
            except Exception as e:
                logging.error(f"Erro durante a observação: {e}")
            time.sleep(300)  # Espera 5 minutos antes de verificar novamente

    def check_and_update_decisions(self):
        """ Iterates through currency pairs and processes each one. """
        currency_pairs = self.currency_pair_service.get_currency_pairs()
        for pair in currency_pairs:
            self.process_pair(pair)

    def process_pair(self, pair):
        """ Processes a single currency pair for trading decisions. """
        try:
            prices = self.fetch_price_data(pair)
            if self.are_prices_sufficient(prices):
                self.evaluate_and_update_decision(pair, prices)
        except Exception as e:
            logging.error(f"Erro ao processar {pair}: {e}")

    def fetch_price_data(self, pair):
        """ Fetches price data for different time intervals. """
        return (
            self.currency_pair_service.fetch_price_data(pair, "5min"),
            self.currency_pair_service.fetch_price_data(pair, "15min"),
            self.currency_pair_service.fetch_price_data(pair, "1h")
        )

    def are_prices_sufficient(self, prices):
        """ Checks if the fetched prices are sufficient for decision making. """
        return all(len(price) >= 14 for price in prices)

    def evaluate_and_update_decision(self, pair, prices):
        """ Evaluates and updates the trading decision for a currency pair. """
        decision, indicators = self.decision_service.make_decision(pair, *prices)
        if self.last_decisions.get(pair) != decision:
            logging.info(f"Decisão alterada para {pair}: {decision}")
            self.last_decisions[pair] = decision
            self.save_decision(pair, decision, indicators)

    def save_decision(self, currency_pair, decision, indicators):
        """ Saves the trading decision and updates the learning service. """
        TradingDecision.objects.create(currency_pair=currency_pair, decision=decision)
        success = decision in ["Compra", "Venda"]
        self.learning_service.store_result(indicators, success)

    def stop_observer(self):
        """ Stops the observer thread. """
        self.running = False
        if self.observer_thread.is_alive():
            self.observer_thread.join()
