from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket, ProductoTicket
import requests
import openpyxl
from django.http import HttpResponse
from decimal import Decimal


def postventa(request):
    ticket = Ticket.objects.filter(estado='PENDIENTE').last()
    if not ticket:
        ticket = Ticket.objects.create()
    productos = ticket.productos.all()

    # Total sin descuento
    total = ticket.total

    # Cantidad total de productos (sumando cantidades)
    cantidad_total = sum(p.cantidad for p in productos)

    # Lógica de descuento y mensaje
    descuento = 0
    mensaje_descuento = ''
    color_mensaje = ''

    if cantidad_total >= 4:
        descuento = total * Decimal('0.05')
        total_con_descuento = total - descuento
        mensaje_descuento = "¡Genial! Has conseguido un descuento del 5%."
        color_mensaje = "green"
    else:
        faltan = 4 - cantidad_total
        total_con_descuento = total
        mensaje_descuento = f"Te faltan {faltan} producto(s) para tener un descuento del 5%."
        color_mensaje = "red"

    context = {
        'ticket': ticket,
        'productos': productos,
        'total': total,
        'total_con_descuento': total_con_descuento,
        'descuento': descuento,
        'mensaje_descuento': mensaje_descuento,
        'color_mensaje': color_mensaje,
    }
    return render(request, 'postventa.html', context)


@csrf_exempt
def agregar_producto(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        codigo = request.POST.get('codigo_producto', '').strip()

        if not codigo:
            return render(request, 'postventa.html', {
                'error': 'Debe ingresar el código del producto.',
                'ticket': ticket,
                'productos': ticket.productos.all(),
                'total': ticket.total,
            })

        url_api = f'http://localhost:8003/products/code/{codigo}'

        try:
            resp = requests.get(url_api, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            nombre = data.get('name')
            precio = float(data.get('price'))
            stock = int(data.get('stock'))

            if stock <= 0:
                return render(request, 'postventa.html', {
                    'error': f'El producto "{nombre}" no tiene stock disponible.',
                    'ticket': ticket,
                    'productos': ticket.productos.all(),
                    'total': ticket.total,
                })

        except Exception as e:
            return render(request, 'postventa.html', {
                'error': f'No existe producto con código "{codigo}".',
                'ticket': ticket,
                'productos': ticket.productos.all(),
                'total': ticket.total,
            })

        # Agregar o incrementar el producto en el ticket
        producto_ticket = ticket.productos.filter(codigo=codigo).first()
        if producto_ticket:
            if producto_ticket.cantidad + 1 > stock:
                return render(request, 'postventa.html', {
                    'error': f'No hay suficiente stock para agregar más unidades de "{nombre}".',
                    'ticket': ticket,
                    'productos': ticket.productos.all(),
                    'total': ticket.total,
                })
            producto_ticket.cantidad += 1
            producto_ticket.save()
        else:
            ProductoTicket.objects.create(
                ticket=ticket,
                codigo=codigo,
                nombre=nombre,
                precio=precio,
                cantidad=1
            )

        # Recalcular total
        ticket.total = sum(p.total for p in ticket.productos.all())
        ticket.save()

        return redirect('postventa')

    return redirect('postventa')


def limpiar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.productos.all().delete()
    ticket.total = 0
    ticket.save()
    return redirect('postventa')


def cobrar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    productos = ticket.productos.all()

    # Calcula cantidad total para descuento
    cantidad_total = sum(p.cantidad for p in productos)
    total = ticket.total

    if cantidad_total >= 4:
        descuento = total * Decimal('0.05')
        total_con_descuento = total - descuento
    else:
        total_con_descuento = total

    # Actualiza stock via API (igual que antes)
    for producto in productos:
        url_stock = f'http://localhost:8003/products/update_stock/{producto.codigo}/'
        try:
            resp = requests.post(url_stock, params={'cantidad': producto.cantidad}, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            return render(request, 'postventa.html', {
                'error': f'No se pudo actualizar el stock de "{producto.nombre}". Error: {e}',
                'ticket': ticket,
                'productos': productos,
                'total': ticket.total,
            })

    # Guardar el total con descuento en el ticket
    ticket.total = total_con_descuento
    ticket.estado = 'COBRADO'
    ticket.save()

    # Crear nuevo ticket vacío para seguir trabajando
    Ticket.objects.create()
    return redirect('postventa')


def modificar_cantidad(request, ticket_id, producto_id, accion):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    producto = get_object_or_404(ProductoTicket, id=producto_id, ticket=ticket)

    if accion == 'sumar':
        producto.cantidad += 1
    elif accion == 'restar' and producto.cantidad > 1:
        producto.cantidad -= 1
    producto.save()

    ticket.total = sum(p.total for p in ticket.productos.all())
    ticket.save()

    return redirect('postventa')



def detalle_lista(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    productos = ticket.productos.all()  # ajusta según tu modelo

    return render(request, 'detallelista.html', {
        'ticket': ticket,
        'productos': productos,
    })


def historial_postventa(request):
    tickets = Ticket.objects.filter(estado='COBRADO') 
    return render(request, 'historialpostventa.html', {'tickets': tickets})



def detalle_ticket_postventa(request, ticket_id):
    # Obtener el ticket o 404 si no existe
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Obtener los productos relacionados a ese ticket
    productos = ProductoTicket.objects.filter(ticket=ticket)

    context = {
        'ticket': ticket,
        'productos': productos,
    }
    # Renderizar con la plantilla correcta
    return render(request, 'detallehistorial.html', context)

def finalizar_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.pedido_completado = True
        ticket.save()
        return redirect('detalle_lista', ticket_id=ticket_id)  # o a donde quieras redirigir después
    # Si no es POST, redirige o muestra error
    return redirect('detalle_lista', ticket_id=ticket_id)




def lista_bodeguero(request):
    tickets = Ticket.objects.filter(estado='COBRADO', pedido_completado=False).order_by('-id')
    return render(request, 'listabodeguero.html', {
        'tickets': tickets
    })

def finalizar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.pedido_completado = True
    ticket.save()
    return redirect('lista_bodeguero')  # o donde quieras redirigir después de finalizar



def alerta_stock(request):
    api_url = 'http://localhost:8003/low-stock'  # URL de tu API FastAPI

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        productos = response.json()
    except requests.RequestException:
        productos = []

    return render(request, 'alertarstock.html', {'productos': productos})

# exportar exel ticket
def exportar_tickets_excel(request):
    # Crear un libro de Excel y una hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tickets"

    # Encabezados de columnas
    ws.append([
        "ID Ticket",
        "Fecha Creación",
        "Total Ticket",
        "Código Producto",
        "Nombre Producto",
        "Cantidad Producto",
    ])

    tickets = Ticket.objects.all().prefetch_related('productos')

    for ticket in tickets:
        for producto in ticket.productos.all():
            ws.append([
                ticket.id,
                ticket.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if ticket.fecha_creacion else "",
                ticket.total,
                producto.codigo,
                producto.nombre,
                producto.cantidad,
            ])

    # Preparar respuesta HTTP con Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=tickets.xlsx'
    wb.save(response)
    return response