from django.contrib import admin
from .models import Product
# Register your models here.


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product_id', 'admin_url',
                    'recomendation_price', 'min_price', 'mode']
    list_editable = ['name', 'product_id', 'recomendation_price', 'min_price', 'mode']