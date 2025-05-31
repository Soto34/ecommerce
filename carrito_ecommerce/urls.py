# URLS
from django.urls import path
from . import views

urlpatterns = [
    path('agregar-producto/', views.agregar_producto, name='add_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('finalizar/', views.finalizar_compra, name='finalizar_compraecommerce'),
    path('validar-pago/<int:ticket_id>/', views.validar_pago, name='validar_pago'),
    path('bodeguero/', views.lista_bodeguero, name='lista_bodegueroecommerce'),
    path('cambiar-estado-envio/<int:ticket_id>/', views.cambiar_estado_envio, name='cambiar_estado_envio'),



     # Acciones del carrito
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),


    path('contador/', views.vista_contador, name='vista_contador'),


    path('cambiar-estado-envio2/<int:ticket_id>/', views.cambiar_estado_envio2, name='cambiar_estado_envio2'),
    path('repartidor/', views.lista_repartidor, name='lista_repartidor'),


    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
 


]
