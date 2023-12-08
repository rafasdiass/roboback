from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Importações dos serviços usando o nome do aplicativo
from services.robo_service import RoboService
from services.currency_pair_service import CurrencyPairService
from services.decision_service import DecisionService
from services.api_service import APIService
from services.learning_service import LearningService

# Inicialização dos serviços
api_service = APIService('NB19FGHNM74Q9QAU')
learning_service = LearningService()
decision_service = DecisionService()
currency_pair_service = CurrencyPairService(api_service)
robo_service = RoboService(decision_service, currency_pair_service, learning_service)

@require_http_methods(["GET"])
def get_robo_decisions(request):
    try:
        decisions = robo_service.get_latest_decisions()
        decisions_data = [
            {'currencyPair': d.currencyPair, 'decision': d.decision, 'time': d.time}
            for d in decisions
        ]
        return JsonResponse({'decisions': decisions_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_currency_pair_data(request):
    try:
        symbol = request.GET.get('symbol', 'EURUSD')
        interval = request.GET.get('interval', '5min')
        currency_pair_data = currency_pair_service.fetch_price_data(symbol, interval)
        # A serialização dos dados depende de como os dados são estruturados.
        # Este é um exemplo genérico de como você poderia serializar os dados.
        currency_pair_data_serializable = {
            'symbol': symbol,
            'data': currency_pair_data  # Supondo que esta é a estrutura que você precisa
        }
        return JsonResponse(currency_pair_data_serializable)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
