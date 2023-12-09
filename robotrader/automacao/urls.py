from django.urls import path
from .views import RoboDecisionsView, CurrencyPairDataView

urlpatterns = [
    path('decisoes-robo/', RoboDecisionsView.as_view(), name='decisoes-robo'),
    path('dados-par-moeda/', CurrencyPairDataView.as_view(), name='dados-par-moeda'),
]
