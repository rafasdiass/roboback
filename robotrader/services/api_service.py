import requests
import logging  # Importação necessária para usar logging.error()
from automacao.models import RoboDecisionModel

class APIService:
    def __init__(self):
        self.decisions_url = 'http://127.0.0.1:8080/api/decisoes-robo'

    def fetch_robo_decisions(self):
        try:
            response = requests.get(self.decisions_url, timeout=10)
            if response.status_code == 200:
                decisions_data = response.json()
                return [RoboDecisionModel(**d) for d in decisions_data]
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {e}")
            raise

    def save_robo_decision(self, currency_pair, decision):
        RoboDecisionModel.objects.create(currency_pair=currency_pair, decision=decision)
        print(f"Decisão salva para {currency_pair}: {decision}")

    def get_saved_decisions(self):
        return list(RoboDecisionModel.objects.all().values())
