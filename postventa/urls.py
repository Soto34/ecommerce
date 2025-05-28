from django.urls import path
from . import views

urlpatterns = [
    path('detalle_lista/<int:ticket_id>/', views.detalle_lista, name='detalle_lista'),


    path('historial_postventa/', views.historial_postventa, name='historial_postventa'),
    path('historial_postventa/ticket/<int:ticket_id>/', views.detalle_ticket_postventa, name='detalle_ticket_postventa'),
    path('postventa/<int:ticket_id>/finalizar/', views.finalizar_ticket, name='finalizar_ticket'),



    path('lista_bodeguero/', views.lista_bodeguero, name='lista_bodeguero'),

    path('postventa/', views.postventa, name='postventa'),
    path('postventa/<int:ticket_id>/agregar/', views.agregar_producto, name='agregar_producto'),
    path('postventa/<int:ticket_id>/limpiar/', views.limpiar_ticket, name='limpiar_ticket'),
    path('postventa/<int:ticket_id>/cobrar/', views.cobrar_ticket, name='cobrar_ticket'),
    path('postventa/<int:ticket_id>/producto/<int:producto_id>/<str:accion>/', views.modificar_cantidad, name='modificar_cantidad'),

    path('alertastock/', views.alerta_stock, name='alerta_stock'),


    path('postventa/exportar_tickets_excel/', views.exportar_tickets_excel, name='exportar_tickets_excel'),

    
]
