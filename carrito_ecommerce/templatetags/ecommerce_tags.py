from django import template
from decimal import Decimal
from ..models import TicketEcommerce

register = template.Library()

@register.simple_tag(takes_context=True)
def obtener_ticket_activo(context):
    request = context['request']
    user = request.user if request.user.is_authenticated else None

    if user:
        ticket = TicketEcommerce.objects.filter(
            user=user,
            es_carrito=True  # ✅ solo tickets activos
        ).last()
        if ticket:
            return ticket

    email_usuario = request.session.get('user_email')
    if email_usuario:
        ticket = TicketEcommerce.objects.filter(
            email_usuario=email_usuario,
            es_carrito=True  # ✅
        ).last()
        if ticket:
            return ticket

    ticket_id = request.session.get('ticket_id')
    if ticket_id:
        ticket = TicketEcommerce.objects.filter(
            id=ticket_id,
            es_carrito=True  # ✅
        ).last()
        if ticket:
            return ticket

    return None


@register.filter
def sumar_subtotales(productos):
    return sum(producto.precio * producto.cantidad for producto in productos)