from django import forms
from .models import TicketEcommerce

class FinalizarCompraForm(forms.ModelForm):
    class Meta:
        model = TicketEcommerce
        fields = ['nombre', 'apellido', 'rut', 'direccion', 'comuna', 'metodo_pago', 'comprobante']

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get("metodo_pago")
        comprobante = cleaned_data.get("comprobante")

        if metodo == 'transferencia' and not comprobante:
            raise forms.ValidationError("Debes subir el comprobante si eliges transferencia.")
