from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
import os
import uuid



API_URL = "http://127.0.0.1:8001/products/"

### Vistas de Productos ###
def products_list(request):
    try:
        response = requests.get("http://127.0.0.1:8001/products")
        products = response.json() if response.status_code == 200 else []
    except Exception as e:
        products = []
        messages.error(request, f"No se pudo conectar a la API: {str(e)}")
    
    return render(request, 'products/products_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            image_url = None
            image_file = request.FILES.get('image')

            if image_file:
                import uuid, os
                filename = f"{uuid.uuid4().hex}_{image_file.name}"
                image_path = os.path.join('media/products', filename)
                with open(image_path, 'wb+') as dest:
                    for chunk in image_file.chunks():
                        dest.write(chunk)
                image_url = request.build_absolute_uri(f"/media/products/{filename}")

            payload = {
                "codigo": form.cleaned_data['codigo'],
                "name": form.cleaned_data['name'],
                "description": form.cleaned_data['description'],
                "price": int(form.cleaned_data['price']),
                "stock": int(form.cleaned_data['stock']),
                "stock_min": int(form.cleaned_data['stock_min']),
                "image": image_url if image_url else "",
                "category_id": form.cleaned_data['category'].id
            }

            try:
                response = requests.post("http://127.0.0.1:8001/products", json=payload)
                if response.status_code in [200, 201]:
                    messages.success(request, 'Producto creado exitosamente')
                    return redirect('products_list')
                else:
                    messages.error(request, f"Error API: {response.json().get('detail')}")
            except Exception as e:
                messages.error(request, f"Error de conexión: {str(e)}")

    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, pk):
    # Obtener datos desde la API
    try:
        response = requests.get(f"{API_URL}{pk}")
        if response.status_code != 200:
            messages.error(request, "Producto no encontrado en la API")
            return redirect('products_list')
        product_data = response.json()
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {str(e)}")
        return redirect('products_list')

    # Si es POST: procesar formulario
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            payload = {
                "codigo": form.cleaned_data['codigo'],
                "name": form.cleaned_data['name'],
                "description": form.cleaned_data['description'],
                "price": int(form.cleaned_data['price']),
                "stock": int(form.cleaned_data['stock']),
                "stock_min": int(form.cleaned_data['stock_min']),
                "image": product_data['image'],  # no se cambia desde aquí
                "category_id": form.cleaned_data['category'].id
            }

            try:
                put_response = requests.put(f"{API_URL}{pk}", json=payload)
                if put_response.status_code == 200:
                    messages.success(request, "Producto actualizado correctamente")
                    return redirect('products_list')
                elif put_response.status_code == 400:
                    error = put_response.json().get("detail", "Error al actualizar")
                    messages.error(request, f"Error: {error}")
                else:
                    messages.error(request, f"Error inesperado ({put_response.status_code})")
            except Exception as e:
                messages.error(request, f"Error al conectar con la API: {str(e)}")
        else:
            messages.error(request, "Formulario inválido")
    
    # Si es GET: mostrar formulario con datos precargados
    else:
        # Obtener categoría existente para precargar correctamente
        try:
            category = Category.objects.get(id=product_data["category_id"])
        except Category.DoesNotExist:
            category = None

        initial_data = {
            "codigo": product_data["codigo"],
            "name": product_data["name"],
            "description": product_data["description"],
            "price": product_data["price"],
            "stock": product_data["stock"],
            "stock_min": product_data["stock_min"],
            "category": category,
        }

        form = ProductForm(initial=initial_data)

    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product_data
    })

def product_delete(request, pk):
    if request.method == 'POST':
        try:
            response = requests.delete(f"http://127.0.0.1:8001/products/{pk}")
            if response.status_code == 200:
                messages.success(request, 'Producto eliminado correctamente')
            else:
                messages.error(request, f"Error: {response.json().get('detail')}")
        except Exception as e:
            messages.error(request, f"Error de conexión: {str(e)}")

    return redirect('products_list')


    

### Vistas de Categorías ###
def categories_list(request):
    categories = Category.objects.annotate(product_count=Count('product'))

    if not categories.exists():
        messages.info(request, 'No hay categorías registradas')

    # Paginación de 10 categorías por página
    paginator = Paginator(categories, 10)
    page = request.GET.get('page')

    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    return render(request, 'products/categories_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoría "{category.name}" creada')
            return redirect('categories_list')
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    
    else:
        form = CategoryForm()
    
    return render(request, 'products/category_form.html', {'form': form})

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoría "{category.name}" actualizada')
            return redirect('categories_list')
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'products/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        if category.product_set.exists():
            messages.error(request, 'No se puede eliminar: tiene productos asociados')
        else:
            category.delete()
            messages.success(request, 'Categoría eliminada')
    return redirect('categories_list')
        
    
# Catalogo
def catalogo(request):
    try:
        response = requests.get("http://127.0.0.1:8001/products")
        if response.status_code == 200:
            product_list = response.json()
        else:
            messages.error(request, f"Error al obtener productos desde la API: {response.status_code}")
            product_list = []
    except Exception as e:
        messages.error(request, f"Error de conexión con la API: {str(e)}")
        product_list = []

    # Paginación manual en Django (con la lista traída de la API)
    paginator = Paginator(product_list, 6)  # 6 productos por página
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'products/catalogo.html', {'products': products})



def detail(request, pk):
    try:
        response = requests.get(f"http://127.0.0.1:8001/products/{pk}")
        if response.status_code == 200:
            product = response.json()
        else:
            messages.error(request, "Producto no encontrado en la API")
            return redirect('catalogo')
    except Exception as e:
        messages.error(request, f"Error de conexión con la API: {str(e)}")
        return redirect('catalogo')

    return render(request, 'products/product_detail.html', {'product': product})