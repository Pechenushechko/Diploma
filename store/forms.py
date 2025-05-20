# store/forms.py
from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(label='Название')
    description = forms.CharField(widget=forms.Textarea, label='Описание')
    price = forms.DecimalField(label='Цена')
    image = forms.ImageField(label='Изображение')
