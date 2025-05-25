from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('product/<str:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<str:product_id>/delete/', views.delete_product, name='delete_product'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),

]

