from django import forms
from .models import Product, Category
import requests
from django.core.exceptions import ValidationError

API_URL = "http://127.0.0.1:8003/products/"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['codigo','name', 'description', 'price', 'stock','stock_min', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'codigo': 'Codigo',
            'name': 'Nombre del Producto',
            'description': 'Descripción',
            'price': 'Precio',
            'stock': 'Stock',
            'stock_min' : 'Alerta de Stock',
            'category': 'Categoría',
            'image': 'Imagen'
        }

    


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Nombre de la Categoría'
        }