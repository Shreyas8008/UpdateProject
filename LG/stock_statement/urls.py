from django.urls import path
from .views import stock_statement
from stock_statement import views


urlpatterns = [
    path('stock-statement/', views.stock_statement, name='stock_statement'),
]
