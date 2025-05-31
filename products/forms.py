from django import forms
from .models import Product, Category
from user.models import CustomUser

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['codigo', 'name', 'description', 'price', 'stock', 'stock_min', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'codigo': 'Código',
            'name': 'Nombre del Producto',
            'description': 'Descripción',
            'price': 'Precio',
            'stock': 'Stock',
            'stock_min': 'Alerta de Stock',
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

class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        required=False,  # Para edición, dejar vacío si no se quiere cambiar
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'nombre', 'apellido', 'rut', 'rol', 'password']
        labels = {
            'email': 'Correo electrónico',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'rut': 'RUT',
            'rol': 'Rol',
            'password': 'Contraseña',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Validar que las contraseñas coincidan si se ingresan
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
