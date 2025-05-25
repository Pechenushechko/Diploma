from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
import logging
from .forms import ProductForm
from .models import Product, ProductLog
from datetime import datetime
from django.core.files.storage import default_storage
from django.http import Http404
from mongoengine.errors import DoesNotExist


logger = logging.getLogger('product')

def home(request):
    return render(request, 'store/home.html')

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    return render(request, 'store/contact.html')

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES['image']
            image_path = default_storage.save(f'products/{img.name}', img)
         
           
            product = Product(
                name=form.cleaned_data['name'],
                description=form.cleaned_data.get('description', ''),
                price=form.cleaned_data.get('price', 0),
                image=image_path
            )
            product.save()

            # Лог в MongoDB
            ProductLog(
                product_id=str(product.id),
                action='created',
                user=str(request.user),
                timestamp=datetime.utcnow(),
                details=f'Создан товар: {product.name}'
            ).save()

            # Лог в файл
            logger.info(f"User: {request.user} Add product: {product.name} (ID: {product.id})")

            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'store/add_product.html', {'form': form})

@staff_member_required
def edit_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        raise Http404("Товар не найден")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product.name = form.cleaned_data['name']
            product.description = form.cleaned_data.get('description', '')
            product.price = form.cleaned_data.get('price', 0)

            if 'image' in request.FILES:
                img = request.FILES['image']
                image_path = default_storage.save(f'products/{img.name}', img)
                product.image = image_path

            product.save()

            ProductLog(
                product_id=str(product.id),
                action='updated',
                user=str(request.user),
                timestamp=datetime.utcnow(),
                details=f'Изменён товар: {product.name}'
            ).save()

            logger.info(f"User {request.user} updated product: {product.name} (ID: {product.id})")

            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(initial={
            'name': product.name,
            'description': product.description,
            'price': product.price,
        })

    return render(request, 'store/edit_product.html', {'form': form, 'product': product})



@staff_member_required
@require_POST
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        raise Http404("Товар не найден")
    
    product_name = product.name
    product.delete()

    # Логируем удаление
    ProductLog(
        product_id=str(product_id),
        action='deleted',
        user=str(request.user),
        timestamp=datetime.utcnow(),
        details=f'Удалён товар: {product_name}'
    ).save()

    logger.info(f"User {request.user} deleted product: {product_name} (ID: {product_id})")

    return redirect('product_list')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        return render(request, 'store/product_not_found.html', status=404)
    
    return render(request, 'store/product_detail.html', {'product': product})

