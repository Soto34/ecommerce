from django.shortcuts import render, redirect
from .forms import DatosEnvioForm, MetodoPagoForm
from .models import Pedido

def datos_envio_view(request):
    if request.method == 'POST':
        form = DatosEnvioForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            request.session['pedido_id'] = None  # limpiar por si acaso
            pedido.save()
            request.session['pedido_id'] = pedido.id
            return redirect('metodo_pago')
    else:
        form = DatosEnvioForm()
    return render(request, 'pedidos/datos_envio.html', {'form': form})

def metodo_pago_view(request):
    pedido_id = request.session.get('pedido_id')
    if not pedido_id:
        return redirect('datos_envio')

    pedido = Pedido.objects.get(id=pedido_id)

    if request.method == 'POST':
        form = MetodoPagoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            del request.session['pedido_id']  # limpiar después del pedido
            return redirect('pedido_confirmado')
    else:
        form = MetodoPagoForm(instance=pedido)
    return render(request, 'pedidos/metodo_pago.html', {'form': form})

def pedido_confirmado_view(request):
    return render(request, 'pedido_confirmado.html')
