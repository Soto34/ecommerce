import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product

def calculate_cart_total(cart):
    """Función auxiliar para calcular el total del carrito"""
    return sum(
        float(item['price']) * int(item['quantity'])
        for item in cart.values()
    )

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product_key = str(product.id)

    # Obtener la URL correcta de la imagen
    image_url = product.image.url if product.image else None
    
    if product_key in cart:
        cart[product_key]['quantity'] += 1
    else:
        cart[product_key] = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': {  # Estructura más completa para la imagen
                'url': image_url,
                'name': product.image.name if product.image else None
            }
        }

    request.session['cart'] = cart
    request.session['cart_total'] = calculate_cart_total(cart)
    request.session.modified = True
    messages.success(request, f"{product.name} añadido al carrito!")
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))

def cart_view(request):
    cart = request.session.get('cart',{})
    items = []
    total = 0

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = float(item_data['price'] * int(item_data['quantity']))
            items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'subtotal': subtotal,
                'product_key': product_id
            })
            total += subtotal
        except (Product.DoesNotExist, KeyError, ValueError):
            continue

    # Actualiza el total en la sesión
    request.session['cart_total'] = total
    request.session.modified = True

    context = {
        'items': items,
        'total': total,
        'cart_empty': len(items) == 0
    }
    return render(request, 'cart\cart_view.html', context)



def clear_cart(request):
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        return JsonResponse({'success': True, 'message': 'Carrito vacío'})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=400)

# views.py
def update_cart_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = str(data.get('product_id'))
            action = data.get('action')
            
            cart = request.session.get('cart', {})
            
            if action == 'increment':
                cart[product_id]['quantity'] += 1
            elif action == 'decrement':
                if cart[product_id]['quantity'] > 1:
                    cart[product_id]['quantity'] -= 1
            elif action == 'remove':
                cart.pop(product_id, None)
            
            request.session['cart'] = cart
            request.session.modified = True
            
            # Calcular totales
            total_items = sum(item['quantity'] for item in cart.values())
            cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
            
            return JsonResponse({
                'success': True,
                'total_items': total_items,
                'cart_total': cart_total,
                'items': cart  # Enviamos todos los items para actualización
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)    

from django.template.loader import render_to_string
from django.http import HttpResponse
def cart_dropdown_content(request):
    cart = request.session.get('cart', {})
    context = {
        'request': request,
        'cart': cart,
        'cart_total': sum(item['price'] * item['quantity'] for item in cart.values())
    }
    html = render_to_string('includes/cart_dropdown_content.html', context)
    return HttpResponse(html)