from django.urls import path
from . import views

urlpatterns = [
    path('', views.binance_bot, name='binance_bot'),
]