from django.urls import path
from .views import RoboDecisionsView, CurrencyPairDataView

urlpatterns = [
    path('robo-decisions/', RoboDecisionsView.as_view(), name='robo_decisions'),
    path('currency-pair-data/', CurrencyPairDataView.as_view(), name='currency_pair_data'),
]
