from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Categorie)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(BarCode)
