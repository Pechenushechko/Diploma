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
from .models import CATEGORY_CHOICES

logger = logging.getLogger('product')

# Главная страница

def home(request):
    return render(request, 'store/home.html')

# Страницы о магазине и контакты

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
         
            category = request.POST.get('category')
            if category not in dict(CATEGORY_CHOICES):
                    category = 'Прочее'  # Default category if not provided
            product = Product(
                name=form.cleaned_data['name'],
                description=form.cleaned_data.get('description', ''),
                price=form.cleaned_data.get('price', 0),
                category=category,
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

    return render(request, 'store/add_product.html', {
    'form': form,
    'CATEGORY_CHOICES': CATEGORY_CHOICES
})


@staff_member_required
def edit_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Товар не найден")

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price', '0')
        category = request.POST.get('category')

        if category not in dict(CATEGORY_CHOICES):
             return render(request, 'store/edit_product.html', {
                'product': product,
                'category_choices': CATEGORY_CHOICES,
                'error': 'Недопустимая категория',
                'initial': request.POST,
            })

        # Обновление полей
        product.name = name
        product.description = description
        product.price = float(price)
        product.category = category

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

        return redirect('product_list')

    # GET-запрос
    return render(request, 'store/edit_product.html', {
        'product': product,
        'category_choices': CATEGORY_CHOICES,
        'initial': {
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category,
        }
    })




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

# Product listing and detail views

def product_list(request):
    category_filter = request.GET.get('category')
    sort = request.GET.get('sort')
    query = request.GET.get('q')

    products = Product.objects.all()

    if category_filter:
        products = products.filter(category=category_filter)

    if query:
        products = products.filter(name__icontains=query)

    if sort == 'price_asc':
        products = sorted(products, key=lambda p: p.price)
    elif sort == 'price_desc':
        products = sorted(products, key=lambda p: -p.price)

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': [c[0] for c in CATEGORY_CHOICES],
        'selected_category': category_filter,
        'selected_sort': sort,
        'query': query or '',
    })


def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        return render(request, 'store/product_not_found.html', status=404)
    
    return render(request, 'store/product_detail.html', {'product': product})

