# automacao/views.py
import pandas as pd
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.robo_service import RoboService
from services.currency_pair_service import CurrencyPairService
from services.decision_service import DecisionService
from services.api_service import APIService
from services.learning_service import LearningService
from services.chart_data_service import ChartDataService

# Chave de API passada diretamente (não recomendado para produção)
api_key = "RRONFZFN9BJ8HWZK"

# Inicialização dos serviços
api_service = APIService()
chart_data_service = ChartDataService(api_key) 
currency_pair_service = CurrencyPairService(chart_data_service)
decision_service = DecisionService()
learning_service = LearningService()
robo_service = RoboService(decision_service, currency_pair_service, learning_service, api_service)

class RoboDecisionsView(APIView):
    def get(self, request):
        try:
            decisions = robo_service.get_latest_decisions()
            decisions_data = [
                {'currencyPair': d.currencyPair, 'decision': d.decision, 'time': d.time}
                for d in decisions
            ]
            return Response({'decisions': decisions_data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrencyPairDataView(APIView):
    def get(self, request):
        try:
            symbol = request.query_params.get('symbol', 'EURUSD')
            interval = request.query_params.get('interval', '5min')
            currency_pair_data = currency_pair_service.fetch_price_data(symbol, interval)

            # Verifique se os dados são um DataFrame do pandas e converta-os para um formato serializável
            if isinstance(currency_pair_data, pd.DataFrame):
                currency_pair_data_serializable = currency_pair_data.to_dict(orient='records')
            else:
                currency_pair_data_serializable = currency_pair_data  # Se não for um DataFrame, assuma que é serializável

            return Response({'symbol': symbol, 'data': currency_pair_data_serializable})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
