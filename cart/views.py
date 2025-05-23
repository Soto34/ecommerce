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
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = float(item_data['price']) * int(item_data['quantity'])
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
    return render(request, 'cart/view_cart.html', context)

def delete_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        product_name = cart[product_key]['name']
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"{product_name} eliminado del carrito")
    
    return redirect('cart_view')

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product_key = str(product_id)
        cart = request.session.get('cart', {})
        
        if product_key in cart:
            if quantity > 0:
                cart[product_key]['quantity'] = quantity
                messages.success(request, f"Cantidad de {cart[product_key]['name']} actualizada")
            else:
                # Si la cantidad es 0 o menor, eliminamos el producto
                product_name = cart[product_key]['name']
                del cart[product_key]
                messages.success(request, f"{product_name} eliminado del carrito")
            
            request.session['cart'] = cart
            request.session.modified = True
    
    return redirect('cart_view')

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
        messages.success(request, "Carrito vaciado correctamente")
    
    return redirect('cart_view')