from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponseForbidden
import logging
from bson import ObjectId

from .forms import ProductForm
from .models import Product, ProductLog, Order, OrderItem, Review
from datetime import datetime
from django.core.files.storage import default_storage
from mongoengine.errors import DoesNotExist
from django.shortcuts import get_object_or_404
from .models import CATEGORY_CHOICES, ORDER_STATUSES

logger = logging.getLogger('product')

# Главная страница

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
    
    reviews = Review.objects(product=product)

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    user_review = Review.objects(product=product, session_key=session_key).first()
    context = {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'user_has_reviewed': bool(user_review),
    }
    return render(request, 'store/product_detail.html', context)
    return render(request, 'store/product_detail.html', {'product': product})

@require_POST
def add_to_cart(request, product_id):
    qty = int(request.POST.get('quantity', 1))
    cart = get_cart(request)  # <-- теперь всегда словарь
    cart[product_id] = cart.get(product_id, 0) + qty
    save_cart(request, cart)
    return redirect('product_list')

@require_POST
def update_cart(request, product_id):
    qty = int(request.POST.get('quantity', 1))
    cart = get_cart(request)
    if qty <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = qty
    save_cart(request, cart)
    return JsonResponse({'status': 'ok'})

@require_POST
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    if product_id in cart:
        cart.pop(product_id)
    save_cart(request, cart)
    return JsonResponse({'status': 'ok'})

def get_cart(request):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        # если по ошибке записан список — сбрасываем корзину
        cart = {}
    return cart

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def cart_view(request):
    cart = get_cart(request)
    products = []
    total = 0
    for prod_id, qty in cart.items():
        try:
            product = Product.objects.get(id=prod_id)
            subtotal = product.price * qty
            products.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal,
            })
            total += subtotal
        except DoesNotExist:
            continue

    if request.method == 'POST':
        # Оформление заказа
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not (full_name and phone and address):
            return render(request, 'store/cart.html', {
                'products': products,
                'total': total,
                'error': 'Пожалуйста, заполните все поля для оформления заказа.',
            })

        # Формируем список OrderItem
        items = []
        for p in products:
            items.append(OrderItem(
                product_id=p['product'].id,
                name=p['product'].name,
                price=p['product'].price,
                quantity=p['quantity']
            ))

        order = Order(
            user_id=str(request.user.id) if request.user.is_authenticated else None,
            items=items,
            full_name=full_name,
            phone=phone,
            address=address,
            total_price=total,
        )
        order.save()

        # Очистить корзину после оформления
        save_cart(request, {})

        return render(request, 'store/cart.html', {
            'products': [],
            'total': 0,
            'success': 'Заказ успешно оформлен! Спасибо за покупку.',
        })

    return render(request, 'store/cart.html', {
        'products': products,
        'total': total,
    })

@staff_member_required
def order_list(request):
    orders = Order.objects.order_by('-created_at')
    return render(request, 'store/order_list.html', {
        'orders': orders,
        'statuses': ORDER_STATUSES
    })

@staff_member_required
def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Новый', 'В обработке', 'Доставлен', 'Отменён']:
            order.status = new_status
            order.save()
    return redirect('order_list')

def add_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        return render(request, 'store/product_not_found.html', status=404)
   
    # Убедимся, что у сессии есть ключ
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # Проверка: уже оставлял отзыв?
    existing = Review.objects(product=product, session_key=session_key).first()
    if existing:
        # Можно обновить или отклонить
        return redirect('product_detail', product_id=product_id)

    rating = int(request.POST.get('rating'))
    comment = request.POST.get('comment')

    Review(
        product=product,
        session_key=session_key,
        rating=rating,
        comment=comment
    ).save()

    return redirect('product_detail', product_id=product_id)

@require_POST
def delete_review(request, product_id, review_id):
    try:
        review = Review.objects.get(id=ObjectId(review_id))
    except DoesNotExist:
        return redirect('product_detail', product_id=product_id)

    # Проверка авторства по ключу сессии
    if review.session_key != request.session.session_key:
        return redirect('product_detail', product_id=product_id)

    review.delete()
    return redirect('product_detail', product_id=product_id)


def edit_review(request, review_id):
   def edit_review(request, product_id, review_id):
    review = get_object_or_404(Review, id=ObjectId(review_id))

    if review.session_key != request.session.session_key:
        return HttpResponseForbidden("Недоступно")

    if request.method == "POST":
        data = json.loads(request.body)
        review.rating = int(data.get('rating', review.rating))
        review.comment = data.get('comment', review.comment)
        review.save()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid method'}, status=400)

# def reset_cart(request):
#     request.session['cart'] = {}
#     return JsonResponse({'status': 'cart cleared'})

