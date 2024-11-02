import requests
import logging
from automacao.models import RoboDecisionModel

class APIService:
    def __init__(self):
        self.decisions_url = 'http://127.0.0.1:8080/api/decisoes-robo'

    def fetch_robo_decisions(self):
        try:
            response = requests.get(self.decisions_url, timeout=10)
            response.raise_for_status()
            decisions_data = response.json()
            return [RoboDecisionModel(**d) for d in decisions_data]
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {e}")
            raise
        except Exception as e:
            logging.error(f"General Error: {e}")
            raise

    def save_robo_decision(self, currency_pair, decision):
        try:
            RoboDecisionModel.objects.create(currency_pair=currency_pair, decision=decision)
            logging.info(f"Decisão salva para {currency_pair}: {decision}")
        except Exception as e:
            logging.error(f"Erro ao salvar decisão: {e}")

    def get_saved_decisions(self):
        try:
            return list(RoboDecisionModel.objects.all().values())
        except Exception as e:
            logging.error(f"Erro ao recuperar decisões salvas: {e}")
            return []
