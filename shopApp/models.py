from datetime import date
from io import BytesIO

import barcode
from barcode.writer import ImageWriter
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=300, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Categorie(models.Model):
    image = models.ImageField(upload_to='img/categoriesShop/', blank=True)
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.ImageField(upload_to='img/shopPicture/', blank=True)
    name = models.CharField(max_length=200, null=True)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(null=True, decimal_places=2, max_digits=20)
    description = models.CharField(max_length=200, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    tags = models.ForeignKey(Categorie, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_qty = models.IntegerField(default=0, null=False)
    date_created = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    complete = models.BooleanField(default=False)
    date_created = models.DateTimeField(blank=True, null=True)
    transaction_id = models.CharField(max_length=13, null=True, unique=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS, default='Pending')
    delivery_date = models.DateField(null=True, blank=True, default=date.today)

    def __str__(self):
        return '{} {} {}'.format(self.id, self.customer.user.first_name, self.delivery_date)

    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.order.id, self.order.customer.name, self.order.transaction_id)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class BarCode(models.Model):
    barcode = models.ImageField(upload_to='bar_codes/', blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return '{}{}'.format(self.order.customer, self.order.transaction_id)

    def save(self, *args, **kwargs):
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(f'{self.order.transaction_id}', writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode.save(f'{self.order.transaction_id}.png', File(buffer), save=False)
        return super().save(*args, **kwargs)
