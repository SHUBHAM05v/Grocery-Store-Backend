from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart),
    path('add/', views.add_to_cart),
    path('remove/', views.remove_from_cart),
    path('update/', views.update_cart),

    path('wishlist/', views.view_wishlist),
    path('wishlist/add/', views.add_to_wishlist),
    path('wishlist/remove/', views.remove_from_wishlist),
]