import time
from threading import Thread
from automacao.models import TradingDecision
from django.utils import timezone

class RoboService:
    def __init__(self, decision_service, currency_pair_service, learning_service, api_service):
        self.decision_service = decision_service
        self.currency_pair_service = currency_pair_service
        self.learning_service = learning_service
        self.api_service = api_service  # Adicionado para comunicação com o front-end
        self.last_decisions = {}
        self.running = True
        self.observer_thread = Thread(target=self.run_observer)
        self.observer_thread.daemon = True
        self.observer_thread.start()

    def observe_data(self):
        if not self.running:
            self.running = True
            self.observer_thread = Thread(target=self.run_observer)
            self.observer_thread.daemon = True
            self.observer_thread.start()

    def run_observer(self):
        while self.running:
            try:
                self.check_and_update_decisions()
            except Exception as e:
                print(f"Erro durante a observação: {e}")
            time.sleep(300)  # Espera por 5 minutos

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
            # Define os intervalos
            intervals = ["5min", "15min", "1h"]

            # Obtém os dados de preço para cada intervalo
            prices5min = self.currency_pair_service.fetch_price_data(pair, intervals[0])
            prices15min = self.currency_pair_service.fetch_price_data(pair, intervals[1])
            prices1h = self.currency_pair_service.fetch_price_data(pair, intervals[2])

            # Continua com o processamento
            decision, indicators = self.decision_service.make_decision(pair, prices5min, prices15min, prices1h)

            if self.last_decisions.get(pair) != decision:
                print(f"Decisão alterada para {pair}: {decision}")
                self.last_decisions[pair] = decision
                self.save_decision(pair, decision, indicators)
                self.api_service.save_robo_decision(pair, decision)  # Novo método para salvar a decisão

    def save_decision(self, currency_pair, decision, indicators):
        TradingDecision.objects.create(currency_pair=currency_pair, decision=decision)
        success = decision in ["Compra", "Venda"]
        self.learning_service.store_result(indicators, success)

    # Outros métodos conforme necessário
