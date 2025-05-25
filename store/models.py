from mongoengine import Document, StringField, DecimalField, DateTimeField
from datetime import datetime

CATEGORY_CHOICES = [
    ('Корма', 'Корма'),
    ('Аксессуары', 'Аксессуары'),
    ('Игрушки', 'Игрушки'),
    ('Гигиена', 'Гигиена'),
    ('Лекарства', 'Лекарства'),
    ('Прочее', 'Прочее'),
]

class Product(Document): 
    name = StringField(required=True)
    category = StringField(choices= CATEGORY_CHOICES)  # важно!
    description = StringField()
    price = DecimalField()
    image = StringField()

    meta = {
        'collection': 'products',
        'abstract' : False
    }

class ProductLog(Document):
    product_id = StringField()
    action = StringField(choices=['created', 'updated', 'deleted'])
    user = StringField()
    timestamp = DateTimeField(default=datetime.utcnow)
    details = StringField()

    meta = {
        'collection': 'product_logs',
        'abstract' : False
    }
