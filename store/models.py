from mongoengine import Document, StringField, DecimalField, DateTimeField, ListField, FloatField, EmbeddedDocument, fields
from datetime import datetime

CATEGORY_CHOICES = [
    ('Корма', 'Корма'),
    ('Аксессуары', 'Аксессуары'),
    ('Игрушки', 'Игрушки'),
    ('Гигиена', 'Гигиена'),
    ('Лекарства', 'Лекарства'),
    ('Прочее', 'Прочее'),
]

ORDER_STATUSES = ['Новый', 'В обработке', 'Доставлен', 'Отменён']

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

class OrderItem(EmbeddedDocument):
    product_id = fields.ObjectIdField(required=True)
    name = fields.StringField(required=True)
    price = fields.DecimalField(required=True, precision=2)
    quantity = fields.IntField(required=True, min_value=1)

class Order(Document):
    user_id = fields.StringField() # ID пользователя, который сделал заказ
    items = fields.EmbeddedDocumentListField(OrderItem, required=True)
    full_name = fields.StringField(required=True)
    phone = fields.StringField(required=True)
    address = fields.StringField(required=True)
    total_price = FloatField(default=0)
    status = fields.StringField(choices= ORDER_STATUSES, default='Новый')
    created_at = fields.DateTimeField(default=datetime.utcnow)

    def calculate_total(self):
        self.total_price = sum(item.price * item.quantity for item in self.items)
