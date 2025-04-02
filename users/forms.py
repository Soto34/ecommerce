from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from .models import CustomUser

class CustomSignupForm(SignupForm):
    name = forms.CharField(max_length=255, label="Nombre")
    last_name = forms.CharField(max_length=255, label="Apellido")

    def save(self, request):
        user = super().save(request) 
        user.name = self.cleaned_data["name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        # Asignar al grupo Clientes
        group, created = Group.objects.get_or_create(name="Clientes")
        user.groups.add(group)
        return user
