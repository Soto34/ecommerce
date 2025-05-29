from django import forms
from .models import Pedido

class DatosEnvioForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre', 'apellido', 'telefono', 'correo', 'rut', 'direccion', 'comuna', 'region', 'codigo_postal', 'especificaciones']

class MetodoPagoForm(forms.ModelForm):
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODOS_PAGO,  # Usa las opciones del modelo
        widget=forms.RadioSelect,
    )
    
    class Meta:
        model = Pedido
        fields = ['metodo_pago']