from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not item_created:
            item.quantity += 1
            item.save()
        
        print(f"Item creado: {item.id} - Cantidad: {item.quantity}")
        messages.success(request, f"{product.name} added to cart!")
    else:
        cart = request.session.get('cart', {})
        product_key = str(product.id)

        if product_key in cart:
            cart[product_key]['quantity'] += 1
        else:
            # Guardamos los datos EXACTAMENTE como en el carrito autenticado
            cart[product_key] = {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': 1,
                'image_url': product.image.url if product.image else None,
                'product': {  # Estructura similar al modelo Product
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image_url': product.image.url if product.image else None,
                }
            }

        request.session['cart'] = cart
        request.session.modified = True

    messages.success(request, f"{product.name} añadido al carrito!")
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))

@login_required
def cart_view(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            items = cart.items.select_related('product').all()
            total = cart.total  # Usamos el método del modelo
        except Cart.DoesNotExist:
            items = []
            total = 0
    else:
        cart_session = request.session.get('cart', {})
        items = []
        total = 0

        for product_id, item_data in cart_session.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = float(item_data['price']) * int(item_data['quantity'])
                items.append({
                    'product': product,
                    'quantity': item_data['quantity'],
                    'subtotal': subtotal
                })
                total += subtotal
            except (Product.DoesNotExist, KeyError, ValueError):
                continue

        # Guarda el total en la sesión
        request.session['cart_total'] = float(total)
        request.session.modified = True

    context = {
        'items': items,
        'total': total,
        'cart_empty': len(items) == 0
    }
    return render(request, 'cart/view_cart.html', context)

def delete_from_cart(request, product_id):
    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, cart__user=request.user, product_id=product_id)
        product_name = item.product.name
        item.delete()
        messages.success(request, f"{product_name} removed from cart")
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            product_name = cart[str(product_id)]['name']
            del cart[str(product_id)]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, f"{product_name} removed from cart")
    
    return redirect('cart_view')

def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            new_quantity = max(1, int(request.POST.get('quantity', 1)))  # Ensure minimum 1
        except ValueError:
            messages.error(request, "Invalid quantity")
            return redirect('cart_view')

        if request.user.is_authenticated:
            item = get_object_or_404(CartItem, cart__user=request.user, product_id=product_id)
            item.quantity = new_quantity
            item.save()
            messages.success(request, "Quantity updated")
        else:
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] = new_quantity
                request.session['cart'] = cart
                request.session.modified = True
                messages.success(request, "Quantity updated")
            
    return redirect('cart_view')