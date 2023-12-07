# services/robo_service.py

import time
from threading import Thread

class RoboService:
    def __init__(self, decision_service, currency_pair_service, db_service):
        self.decision_service = decision_service
        self.currency_pair_service = currency_pair_service
        self.db_service = db_service  # Serviço para interação com o banco de dados
        self.last_decisions = {}
        self.running = True
        self.observer_thread = Thread(target=self.run_observer)
        self.observer_thread.start()

    def observe_data(self):
        if not self.running:
            self.running = True
            self.observer_thread = Thread(target=self.run_observer)
            self.observer_thread.start()

    def run_observer(self):
        while self.running:
            try:
                self.check_and_update_decisions()
            except Exception as e:
                print(f"Erro durante a observação: {e}")
            time.sleep(300)  # Espera por 5 minutos (300 segundos)

    def stop_observer(self):
        self.running = False
        if self.observer_thread.is_alive():
            self.observer_thread.join()

    def check_and_update_decisions(self):
        currency_pairs = self.currency_pair_service.get_currency_pairs()
        if not currency_pairs:
            print("Nenhum par de moeda disponível para análise.")
            return

        for pair in currency_pairs:
            prices5min, prices15min, prices1h = self.currency_pair_service.fetch_price_data(pair)
            decision = self.decision_service.make_decision(pair, prices5min, prices15min, prices1h)

            if self.last_decisions.get(pair) != decision:
                print(f"Decisão alterada para {pair}: {decision}")
                self.last_decisions[pair] = decision
                self.db_service.save_decision(pair, decision)  # Salvar decisão no banco de dados

    # Outros métodos conforme necessário
