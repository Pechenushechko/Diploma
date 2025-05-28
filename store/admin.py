from django.utils.html import format_html

from django.contrib import admin
from .models import Product

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'image_tag')

#     readonly_fields = ('image_tag',)

#     def image_tag(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
#         return "-"
#     image_tag.short_description = 'Изображение'