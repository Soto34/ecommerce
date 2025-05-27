from django.urls import path
from .views import *



urlpatterns = [
    # Carrito
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('update/<int:product_id>/', update_cart, name='update_cart_ajax'),
    path('remove/<int:product_id>/', delete_from_cart, name='delete_from_cart_ajax'),
    path('clear/', clear_cart, name='clear_cart_ajax')
]

