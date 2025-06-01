from django import forms
from .models import TicketEcommerce
from django.core.exceptions import ValidationError
import re

def validar_rut_chileno(rut):
    rut = rut.upper().replace(".", "").replace("-", "")
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        raise ValidationError("RUT inválido")

    cuerpo = rut[:-1]
    dv = rut[-1]

    suma = sum(int(c) * m for c, m in zip(reversed(cuerpo), [2, 3, 4, 5, 6, 7] * 2))
    dv_calculado = 11 - suma % 11
    dv_calculado = 'K' if dv_calculado == 10 else '0' if dv_calculado == 11 else str(dv_calculado)

    if dv != dv_calculado:
        raise ValidationError("RUT inválido")

class FinalizarCompraForm(forms.ModelForm):
    class Meta:
        model = TicketEcommerce
        fields = ['nombre', 'apellido', 'rut', 'direccion', 'comuna', 'metodo_pago', 'comprobante']

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut_chileno(rut)
        return rut

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get("metodo_pago")
        comprobante = cleaned_data.get("comprobante")

        if metodo == 'transferencia' and not comprobante:
            raise forms.ValidationError("Debes subir el comprobante si eliges transferencia.")
