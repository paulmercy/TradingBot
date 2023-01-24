from django.contrib import admin
from .models import BinanceBot, HistoricalData

admin.site.register(BinanceBot)
admin.site.register(HistoricalData)