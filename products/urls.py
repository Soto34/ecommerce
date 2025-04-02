from django.urls import path
from .views import *



urlpatterns = [
    # Productos
    path('dashboard/', products_list, name='products_list'),
    path('products/add/', product_create, name='product_create'),
    path('products/edit/<int:pk>',product_update, name='product_update'),
    path('products/delete/<int:pk>/', product_delete, name='product_delete'),
    
    # Category URLs
    path('categories/', categories_list, name='categories_list'),
    path('categories/add/', category_create, name='category_create'),
    path('categories/edit/<int:pk>', category_update, name='category_update'),
    path('categories/delete/<int:pk>/', category_delete, name='category_delete')
]

