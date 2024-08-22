from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    product_id = models.IntegerField(unique=True, verbose_name='Артикул')
    admin_url = models.URLField(verbose_name='Ссылка из кабинета')
    default_url = models.URLField(verbose_name='Ссылка API')
    recomendation_price = models.IntegerField(verbose_name='Максимальная желательная цена')
    min_price = models.IntegerField(verbose_name='Минимальная цена')
    price = models.IntegerField(null=True, blank=True, verbose_name='Текущая цена')
    best_price = models.IntegerField(null=True, blank=True, verbose_name='Цена ТОП-1')
    list_position = models.IntegerField(null=True, blank=True, verbose_name='Место в списке')
    mode = models.BooleanField(default=False, verbose_name='Демпинг вкл/выкл')

    def __str__(self):
        return self.name