# VISTAS
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import TicketEcommerce, ProductoTicketEcommerce
from .forms import FinalizarCompraForm
import requests
from decimal import Decimal
from django.contrib import messages

def agregar_producto(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        if not codigo:
            return redirect('catalogo')

        try:
            url = f'http://localhost:8003/products/code/{codigo}'
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            nombre = data.get('name') or data.get('nombre', 'SIN NOMBRE')
            precio = Decimal(data.get('price') or data.get('precio_mayorista', 0))
            stock = int(data.get('stock', 0))

            ticket_id = request.session.get('ticket_id')
            ticket = TicketEcommerce.objects.filter(id=ticket_id, estado_pago='pendiente').last()

            if not ticket:
                ticket = TicketEcommerce.objects.create(nombre='', apellido='', rut='', direccion='', comuna='')
                request.session['ticket_id'] = ticket.id

            producto = ticket.productos.filter(codigo=codigo).first()
            if producto:
                if producto.cantidad < stock:
                    producto.cantidad += 1
                    producto.save()
            else:
                ProductoTicketEcommerce.objects.create(
                    ticket=ticket,
                    codigo=codigo,
                    nombre=nombre,
                    precio=precio,
                    cantidad=1
                )

        except Exception as e:
            print("❌ Error al agregar producto:", e)

    return redirect('ver_carrito')

def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        item = get_object_or_404(ProductoTicketEcommerce, id=item_id)

        if accion == 'incrementar':
            try:
                url = f'http://localhost:8003/products/code/{item.codigo}'
                r = requests.get(url)
                r.raise_for_status()
                data = r.json()
                stock = int(data.get('stock', 0))

                if item.cantidad < stock:
                    item.cantidad += 1
                    item.save()
            except Exception as e:
                print("❌ Error al validar stock:", e)

        elif accion == 'decrementar':
            item.cantidad -= 1
            if item.cantidad <= 0:
                item.delete()
            else:
                item.save()

    return redirect('ver_carrito')

def ver_carrito(request):
    ticket_id = request.session.get('ticket_id')
    ticket = None
    productos = []
    total = Decimal('0.00')
    descuento = Decimal('0.00')
    mensaje_descuento = ''

    if ticket_id:
        ticket = get_object_or_404(TicketEcommerce, id=ticket_id)
        productos = ticket.productos.all()

        for producto in productos:
            producto.subtotal = producto.precio * producto.cantidad
            total += producto.subtotal

        cantidad_total = sum(p.cantidad for p in productos)
        if cantidad_total >= 4:
            descuento = total * Decimal('0.05')
            mensaje_descuento = "¡Tienes un 5% de descuento aplicado!"
            total -= descuento

    context = {
        'ticket': ticket,
        'productos': productos,
        'total': total,
        'descuento': descuento,
        'mensaje_descuento': mensaje_descuento,
    }
    return render(request, 'carrito_ecommerce/carrito.html', context)



def finalizar_compra(request):
    ticket_id = request.session.get('ticket_id')
    ticket = get_object_or_404(TicketEcommerce, id=ticket_id)

    # Calcular totales manualmente igual que en ver_carrito
    productos = ticket.productos.all()
    total = sum(p.precio * p.cantidad for p in productos)
    descuento = Decimal('0.00')
    mensaje_descuento = ''

    cantidad_total = sum(p.cantidad for p in productos)
    if cantidad_total >= 4:
        descuento = total * Decimal('0.05')
        mensaje_descuento = "¡Tienes un 5% de descuento aplicado!"
        total -= descuento

    if request.method == 'POST':
        form = FinalizarCompraForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            metodo_pago = form.cleaned_data['metodo_pago']
            if metodo_pago == 'paypal':
                ticket.estado_pago = 'pagado'
            else:
                ticket.estado_pago = 'pendiente'
                if 'comprobante' in request.FILES:
                    ticket.comprobante = request.FILES['comprobante']
            ticket.save()
            del request.session['ticket_id']
            return HttpResponse("Compra finalizada")
    else:
        form = FinalizarCompraForm(instance=ticket)

    return render(request, 'carrito_ecommerce/finalizar.html', {
        'form': form,
        'ticket': ticket,
        'total': total,
        'descuento': descuento,
        'mensaje_descuento': mensaje_descuento,
    })





def vista_contador(request):
    tickets_pendientes = TicketEcommerce.objects.filter(estado_pago='pendiente')

    resumen = []
    for ticket in tickets_pendientes:
        productos = ticket.productos.all()
        total = sum(p.precio * p.cantidad for p in productos)
        cantidad_total = sum(p.cantidad for p in productos)
        descuento = Decimal('0.00')
        if cantidad_total >= 4:
            descuento = total * Decimal('0.05')
            total -= descuento
        resumen.append({
            'ticket': ticket,
            'productos': productos,
            'total': total,
            'descuento': descuento,
        })

    return render(request, 'carrito_ecommerce/contador.html', {
        'resumen': resumen
    })


def validar_pago(request, ticket_id):
    ticket = get_object_or_404(TicketEcommerce, id=ticket_id, estado_pago='pendiente')
    ticket.estado_pago = 'pagado'
    ticket.save()
    messages.success(request, f"El ticket #{ticket.id} fue marcado como pagado.")
    return redirect('vista_contador')



def lista_bodeguero(request):
    tickets = TicketEcommerce.objects.filter(estado_pago='pagado')
    return render(request, 'carrito_ecommerce/bodeguero.html', {'tickets': tickets})


def cambiar_estado_envio(request, ticket_id):
    ticket = get_object_or_404(TicketEcommerce, id=ticket_id)

    if ticket.estado_envio == 'recolectando productos':
        ticket.estado_envio = 'productos recolectados'
    elif ticket.estado_envio == 'productos recolectados':
        ticket.estado_envio = 'producto entregado'

    ticket.save()
    return redirect('lista_bodegueroecommerce')



def lista_repartidor(request):
    tickets = TicketEcommerce.objects.filter(estado_envio='productos recolectados')
    return render(request, 'carrito_ecommerce/repartidor.html', {'tickets': tickets})

def cambiar_estado_envio2(request, ticket_id):
    ticket = get_object_or_404(TicketEcommerce, id=ticket_id)
    if ticket.estado_envio == 'recolectando productos':
        ticket.estado_envio = 'productos recolectados'
    elif ticket.estado_envio == 'productos recolectados':
        ticket.estado_envio = 'producto entregado'
    ticket.save()
    return redirect('lista_repartidor')
