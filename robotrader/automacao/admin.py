# automacao/admin.py

from django.contrib import admin
from .models import Weight, TradingDecision

admin.site.register(Weight)
admin.site.register(TradingDecision)
