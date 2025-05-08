from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

### Vistas de Productos ###
def products_list(request):
    products = Product.objects.select_related('category').all()
    if not products.exists():
        messages.info(request, 'No hay productos registrados. ¡Crea tu primer producto!')
    return render(request, 'products/products_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Producto "{product.name}" creado con éxito')
            return redirect('products_list')
        
        # Manejo detallado de errores
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Producto "{product.name}" actualizado')
            return redirect('products_list')
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {'form': form, 'product': product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        if product.image:
            product.image.delete(save=False)
        product.delete()
        messages.success(request, 'Producto eliminado correctamente')
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
    products = Product.objects.all()

    # Paginación
    paginator = Paginator(products, 6)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    data = {
        'products':products
    }
    return render(request,'products/catalogo.html',data)


def detail(request,pk):
    product = get_object_or_404(Product, pk=pk)
    data = {
        'product':product
    }
    return render(request,'products/product_detail.html',data)