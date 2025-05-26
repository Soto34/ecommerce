from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
import uuid
import os
from django.conf import settings
from urllib.parse import urlparse


API_URL = "http://127.0.0.1:8003/products/"
API_BASE_URL = "http://localhost:3001/categories"

def delete_product_image(image_url):
    if not image_url:
        return False
    
    try:
        # Parsear la URL para obtener la ruta relativa
        parsed_url = urlparse(image_url)
        if not parsed_url.path.startswith('/media/'):
            print(f"La URL de la imagen no está en el directorio media: {image_url}")
            return False
        
        # Obtener la ruta relativa (ej: "products/filename.jpg")
        relative_path = parsed_url.path[len('/media/'):]
        
        # Construir la ruta completa del sistema de archivos
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        
        # Verificar y eliminar el archivo
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Imagen eliminada correctamente: {full_path}")
            return True
        else:
            print(f"El archivo no existe: {full_path}")
            return False
            
    except Exception as e:
        print(f"Error al eliminar imagen {image_url}: {str(e)}")
        return False


### Vistas de Productos ###
def products_list(request):
    try:
        response = requests.get(f"{API_URL.rstrip('/')}")  # Asegura URL correcta
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

            # Subir imagen al filesystem local
            if image_file:
                filename = f"{uuid.uuid4().hex}_{image_file.name}"
                image_path = os.path.join('media/products', filename)
                
                with open(image_path, 'wb+') as dest:
                    for chunk in image_file.chunks():
                        dest.write(chunk)
                
                image_url = f"/media/products/{filename}"

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
                response = requests.post(f"{API_URL.rstrip('/')}", json=payload)
                
                if response.status_code in [200, 201]:
                    messages.success(request, 'Producto creado exitosamente')
                    return redirect('products_list')
                else:
                    # Si falla la API, borramos la imagen subida
                    if image_url:
                        delete_product_image(image_url)
                    messages.error(request, f"Error API: {response.json().get('detail', 'Error desconocido')}")
            except Exception as e:
                if image_url:
                    delete_product_image(image_url)
                messages.error(request, f"Error de conexión: {str(e)}")
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, pk):
    # Obtener producto actual
    try:
        response = requests.get(f"{API_URL}{pk}")
        if response.status_code != 200:
            messages.error(request, "Producto no encontrado")
            return redirect('products_list')
        product_data = response.json()
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {str(e)}")
        return redirect('products_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_image_url = product_data['image']
            new_image_file = request.FILES.get('image')

            # Procesar nueva imagen si se subió
            if new_image_file:
                # Eliminar imagen anterior si existía
                if product_data['image']:
                    delete_product_image(product_data['image'])

                # Guardar nueva imagen
                filename = f"{uuid.uuid4().hex}_{new_image_file.name}"
                image_path = os.path.join('media/products', filename)
                
                with open(image_path, 'wb+') as dest:
                    for chunk in new_image_file.chunks():
                        dest.write(chunk)
                
                new_image_url = f"/media/products/{filename}"

            payload = {
                "codigo": form.cleaned_data['codigo'],
                "name": form.cleaned_data['name'],
                "description": form.cleaned_data['description'],
                "price": int(form.cleaned_data['price']),
                "stock": int(form.cleaned_data['stock']),
                "stock_min": int(form.cleaned_data['stock_min']),
                "image": new_image_url,
                "category_id": form.cleaned_data['category'].id
            }

            try:
                response = requests.put(f"{API_URL}{pk}", json=payload)
                if response.status_code == 200:
                    messages.success(request, "Producto actualizado correctamente")
                    return redirect('products_list')
                else:
                    # Si falla la actualización, borramos la nueva imagen si se subió
                    if new_image_file and new_image_url != product_data['image']:
                        delete_product_image(new_image_url)
                    messages.error(request, f"Error: {response.json().get('detail', 'Error desconocido')}")
            except Exception as e:
                if new_image_file and new_image_url != product_data['image']:
                    delete_product_image(new_image_url)
                messages.error(request, f"Error al conectar con la API: {str(e)}")
        else:
            messages.error(request, "Formulario inválido")

    else:
        # Precargar formulario con datos existentes
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
            # 1. Obtener el producto para saber si tiene imagen
            get_response = requests.get(f"{API_URL}{pk}")
            if get_response.status_code != 200:
                messages.error(request, "Producto no encontrado")
                return redirect('products_list')
            
            product_data = get_response.json()
            
            # 2. Eliminar la imagen primero si existe
            if product_data.get('image'):
                if not delete_product_image(product_data['image']):
                    messages.warning(request, 'Producto eliminado pero no se pudo borrar la imagen')
            
            # 3. Eliminar el producto de la API
            delete_response = requests.delete(f"{API_URL}{pk}")
            
            if delete_response.status_code == 200:
                messages.success(request, 'Producto eliminado correctamente')
            else:
                messages.error(request, f"Error al eliminar producto: {delete_response.json().get('detail', 'Error desconocido')}")
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error de conexión con la API: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    return redirect('products_list')


### Vistas de Categorías ###
def categories_list(request):
    try:
        response = requests.get(API_BASE_URL)
        response.raise_for_status()
        categories_data = response.json()
    except requests.RequestException:
        messages.error(request, "No se pudieron obtener las categorías desde la API.")
        categories_data = []

    # Paginación
    paginator = Paginator(categories_data, 10)
    page = request.GET.get('page')

    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    return render(request, 'products/categories_list.html', {'categories': categories})


def category_create(request):
    return render(request, 'products/category_form.html')


def category_update(request, pk):
    return render(request, 'products/category_form.html', {
        'category_id': pk
    })

def category_delete(request, pk):
    if request.method == 'POST':
        try:
            response = requests.delete(f"{API_BASE_URL}/{pk}")
            if response.status_code == 404:
                messages.error(request, "No se encontró la categoría.")
            elif response.status_code in [200, 204]:
                messages.success(request, "Categoría eliminada correctamente.")
            else:
                messages.error(request, f"Error al eliminar la categoría. Código: {response.status_code}")
        except requests.RequestException:
            messages.error(request, "Error al eliminar la categoría en la API.")
    else:
        messages.error(request, "Método no permitido.")
    return redirect('categories_list')
        
    
def catalogo(request):
    # Obtener productos desde la API
    try:
        response = requests.get("http://127.0.0.1:8003/products")
        if response.status_code == 200:
            product_list = response.json()
        else:
            messages.error(request, f"Error al obtener productos desde la API: {response.status_code}")
            product_list = []
    except Exception as e:
        messages.error(request, f"Error de conexión con la API: {str(e)}")
        product_list = []

    # Extraer categorías únicas desde los productos
    categories_dict = {}
    for p in product_list:
        # Asumamos que cada producto tiene 'category' con un dict {id, name} o bien 'category_id' y 'category_name'
        # Ajusta según cómo viene en tu JSON
        cat_id = p.get('category', {}).get('id') or p.get('category_id')
        cat_name = p.get('category', {}).get('name') or p.get('category_name')
        if cat_id and cat_name:
            categories_dict[cat_id] = cat_name

    # Convertir a lista de dicts ordenada por nombre
    categories = sorted(
        [{'id': k, 'name': v} for k, v in categories_dict.items()],
        key=lambda x: x['name']
    )

    selected_category = request.GET.get('category', '')

    # Filtrar productos si hay categoría seleccionada
    if selected_category != "":
        product_list = [p for p in product_list if str(p.get('category', {}).get('id', p.get('category_id'))) == selected_category]

    # Paginación
    paginator = Paginator(product_list, 6)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'products/catalogo.html', context)
def detail(request, pk):
    try:
        response = requests.get(f"http://127.0.0.1:8003/products/{pk}")
        if response.status_code == 200:
            product = response.json()
        else:
            messages.error(request, "Producto no encontrado en la API")
            return redirect('catalogo')
    except Exception as e:
        messages.error(request, f"Error de conexión con la API: {str(e)}")
        return redirect('catalogo')

    return render(request, 'products/product_detail.html', {'product': product})