from django.urls import path
from .views import *

urlpatterns = [
    path('datos-envio/', datos_envio_view, name='datos_envio'),
    path('metodo-pago/', metodo_pago_view, name='metodo_pago'),
    path('pedido-confirmado/', pedido_confirmado_view, name='pedido_confirmado'),
]
