from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.sales_report),
    path('low-stock/', views.low_stock_products),
]
