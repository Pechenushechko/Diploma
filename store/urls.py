from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('product/<str:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<str:product_id>/delete/', views.delete_product, name='delete_product'),
    path('favicon.ico', RedirectView.as_view(url=static('images/favicon.ico'), permanent=True)),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('product/<str:product_id>/review/', views.add_review, name='add_review'),
    path('product/<product_id>/reviews/<review_id>/edit/', views.edit_review, name='edit_review'),
    path('product/<product_id>/reviews/<review_id>/delete/', views.delete_review, name='delete_review'),
    path('cart/add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('admin/', admin.site.urls),
    path('dashboard/orders/', views.order_list, name='order_list'),
    path('dashboard/orders/<str:order_id>/update/', views.update_order_status, name='update_order_status'),

    # path('cart/reset/', views.reset_cart),


]

