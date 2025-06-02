from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import TicketEcommerce, ProductoTicketEcommerce
from .forms import FinalizarCompraForm
import requests
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def obtener_ticket_activo(request):
    user = request.user if request.user.is_authenticated else None

    if user:
        ticket = TicketEcommerce.objects.filter(
            user=user,
            estado_pago='pendiente',
            es_carrito=True
        ).last()
        if ticket:
            return ticket

    email_usuario = request.session.get('user_email')
    if email_usuario:
        ticket = TicketEcommerce.objects.filter(
            email_usuario=email_usuario,
            estado_pago='pendiente',
            es_carrito=True
        ).last()
        if ticket:
            return ticket

    ticket_id = request.session.get('ticket_id')
    if ticket_id:
        ticket = TicketEcommerce.objects.filter(
            id=ticket_id,
            estado_pago='pendiente',
            es_carrito=True
        ).last()
        if ticket:
            return ticket

    return None


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

            ticket = obtener_ticket_activo(request)

            if not ticket:
                email_usuario = request.session.get('user_email')

                ticket = TicketEcommerce.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    nombre='', apellido='', rut='', direccion='', comuna='',
                    email_usuario=email_usuario
                )
                if not request.user.is_authenticated:
                    request.session['ticket_id'] = ticket.id

            # ✅ Corrección aquí:
            producto = ProductoTicketEcommerce.objects.filter(ticket=ticket, codigo=codigo).first()

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

    return redirect('catalogo')


def limpiar_carrito(request):
    ticket = obtener_ticket_activo(request)
    
    if ticket:
        # Eliminar todos los productos del carrito
        ticket.productos.all().delete()
        # Opcional: eliminar el ticket también
        # ticket.delete()
        messages.success(request, "El carrito se ha vaciado correctamente")
    else:
        messages.info(request, "No hay productos en el carrito")
    
    return redirect('ver_carrito')  # Redirige a la vista del carrito


def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        item = get_object_or_404(ProductoTicketEcommerce, id=item_id)

        try:
            url = f'http://localhost:8003/products/code/{item.codigo}'
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            stock = int(data.get('stock', 0))
        except Exception as e:
            print("❌ Error al validar stock:", e)
            stock = None

        if accion == 'incrementar':
            if stock is None or item.cantidad < stock:
                item.cantidad += 1
                item.save()
        elif accion == 'decrementar':
            item.cantidad -= 1
            if item.cantidad <= 0:
                item.delete()
            else:
                item.save()

    return redirect('ver_carrito')

def ver_carrito(request):
    ticket = obtener_ticket_activo(request)
    productos = []
    total = Decimal('0.00')
    descuento = Decimal('0.00')
    mensaje_descuento = ''

    if ticket:
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
    ticket = obtener_ticket_activo(request)
    if not ticket:
        return redirect('ver_carrito')

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
        print("✅ POST recibido:", request.POST.dict())

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

            ticket.es_carrito = False  # ✅ Marcar que ya no es carrito
            ticket.save()

            # ✅ Limpiar el ticket de la sesión
            request.session.pop('ticket_id', None)

            return render(request, 'carrito_ecommerce/compra_exitosa.html', {
                'ticket': ticket,
                'total': total,
                'descuento': descuento,
            })
        else:
            print("❌ Errores en el formulario:", form.errors)

            return render(request, 'carrito_ecommerce/finalizar.html', {
                'form': form,
                'ticket': ticket,
                'total': total,
                'descuento': descuento,
                'mensaje_descuento': mensaje_descuento,
            })

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

def mis_pedidos_view(request):
    user_email = request.session.get('user_email')
    print("📧 Email en sesión:", user_email)

    if not user_email:
        messages.error(request, "Debes iniciar sesión para ver tus pedidos.")
        return redirect('user:login')

    pedidos = TicketEcommerce.objects.filter(
        Q(user__email=user_email) | Q(email_usuario=user_email)
    ).order_by('-fecha_creacion')

    return render(request, 'carrito_ecommerce/mis_pedidos.html', {'pedidos': pedidos})