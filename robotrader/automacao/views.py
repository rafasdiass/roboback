import pandas as pd
import logging
import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.robo_service import RoboService
from services.currency_pair_service import CurrencyPairService
from services.decision_service import DecisionService
from services.api_service import APIService
from services.learning_service import LearningService
from services.chart_data_service import ChartDataService

# Inicialização dos serviços
api_service = APIService()
chart_data_service = ChartDataService()
currency_pair_service = CurrencyPairService(chart_data_service)
decision_service = DecisionService()
learning_service = LearningService()
robo_service = RoboService(decision_service, currency_pair_service, learning_service, api_service)

# Função para buscar dados intraday de forma síncrona
def fetch_intraday_data_sync(symbol, interval='1m'):
    try:
        data, source = asyncio.run(chart_data_service.fetch_intraday_data(symbol, interval))
        return data, source
    except Exception as e:
        logging.error(f"Erro ao buscar dados intraday para {symbol} com intervalo {interval}: {e}")
        raise

class RoboDecisionsView(APIView):
    def get(self, request):
        try:
            decisions = robo_service.get_latest_decisions()
            decisions_data = [
                {'currencyPair': d.currency_pair, 'decision': d.decision, 'time': d.time}
                for d in decisions
            ]
            return Response({'decisions': decisions_data})
        except Exception as e:
            logging.error(f"Erro ao obter decisões do robô: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrencyPairDataView(APIView):
    def get(self, request):
        try:
            symbol = request.query_params.get('symbol', 'EURUSD')
            interval = request.query_params.get('interval', '5m')
            if interval not in ['1m', '5m', '1h', '1d']:
                raise ValueError(f"Intervalo inválido: {interval}. Intervalos válidos são: ['1m', '5m', '1h', '1d']")
            currency_pair_data, source = fetch_intraday_data_sync(symbol, interval)
            if isinstance(currency_pair_data, pd.DataFrame):
                currency_pair_data_serializable = currency_pair_data.to_dict(orient='records')
            else:
                currency_pair_data_serializable = currency_pair_data

            return Response({'symbol': symbol, 'data': currency_pair_data_serializable, 'source': source})
        except ValueError as ve:
            logging.error(f"Erro de validação: {ve}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Erro ao obter dados do par de moedas {symbol}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetIntradayData(APIView):
    def get(self, request):
        try:
            symbol = request.query_params.get('symbol', 'EURUSD')
            interval = request.query_params.get('interval', '5m')
            if interval not in ['1m', '5m', '1h', '1d']:
                raise ValueError(f"Intervalo inválido: {interval}. Intervalos válidos são: ['1m', '5m', '1h', '1d']")
            data, source = fetch_intraday_data_sync(symbol, interval)
            if isinstance(data, pd.DataFrame):
                data_serializable = data.to_dict(orient='records')
            else:
                data_serializable = data

            return Response({'symbol': symbol, 'data': data_serializable, 'source': source}, status=status.HTTP_200_OK)
        except ValueError as ve:
            logging.error(f"Erro de validação: {ve}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Erro ao obter dados intraday para {symbol}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
