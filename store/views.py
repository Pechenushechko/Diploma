from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
import logging
from .forms import ProductForm
from .models import Product, ProductLog
from datetime import datetime
from django.core.files.storage import default_storage

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


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


