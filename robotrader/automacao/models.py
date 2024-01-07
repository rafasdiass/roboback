from django.db import models

# Defina esta configuração no seu settings.py
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

class Weight(models.Model):
    indicator = models.CharField(max_length=50, unique=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.indicator}: {self.value}"

class TradingDecision(models.Model):
    currency_pair = models.CharField(max_length=20)
    decision = models.CharField(max_length=10)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency_pair} - {self.decision} at {self.time}"

class RoboDecisionModel(models.Model):
    currency_pair = models.CharField(max_length=20)
    decision = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency_pair} - {self.decision} at {self.time}"

# Aqui está o novo modelo DecisionRecord que você solicitou
class DecisionRecord(models.Model):
    currency_pair = models.CharField(max_length=20)
    decision = models.CharField(max_length=10)  # Exemplo: "Compra" ou "Venda"
    result = models.BooleanField()  # True para sucesso, False para falha
    decision_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency_pair} {self.decision} at {self.decision_time} Result: {'Success' if self.result else 'Failure'}"
