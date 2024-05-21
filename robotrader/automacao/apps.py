import asyncio
from django.apps import AppConfig
from services.chart_data_service import ChartDataService

class AutomacaoConfig(AppConfig):
    name = 'automacao'

    def ready(self):
        # Função para fazer a primeira chamada à API
        asyncio.run(self.initialize_data())

    async def initialize_data(self):
        service = ChartDataService()
        try:
            await service.fetch_intraday_data('EURUSD', interval='5m')
        except Exception as e:
            print(f"Erro ao inicializar dados: {e}")
