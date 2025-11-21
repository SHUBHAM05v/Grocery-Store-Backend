from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout),
    path('', views.order_list),
   # Promo APIs
    path('promo/create/', views.create_promo),
    path('promo/', views.list_promos),
    path('promo/update/<int:id>/', views.update_promo),
    path('promo/delete/<int:id>/', views.delete_promo),
]
