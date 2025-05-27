from django.urls import path
from .views import *



urlpatterns = [
    # Carrito
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('clear/', clear_cart, name='clear_cart_ajax'),
    path('cart_view/',cart_view,name="cart_view"),
    
    path('update-item/', update_cart_item, name='update_cart_item'),
    path('cart-dropdown-content/', cart_dropdown_content, name='cart_dropdown_content'),
]

