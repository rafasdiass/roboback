from django.urls import path
from .views import get_robo_decisions, get_currency_pair_data

urlpatterns = [
    # Este caminho é para a função de view que retorna as decisões do robô
    path('decisoes-robo/', get_robo_decisions, name='decisoes-robo'),

    # Este caminho é para a função de view que retorna os dados do par de moedas
    path('dados-par-moeda/', get_currency_pair_data, name='dados-par-moeda'),
]
