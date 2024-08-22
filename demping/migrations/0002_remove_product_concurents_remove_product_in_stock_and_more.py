# Generated by Django 5.1 on 2024-08-22 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("demping", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="concurents",
        ),
        migrations.RemoveField(
            model_name="product",
            name="in_stock",
        ),
        migrations.AlterField(
            model_name="product",
            name="admin_url",
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name="product",
            name="best_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="default_url",
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name="product",
            name="min_price",
            field=models.DecimalField(decimal_places=2, default=False, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="product",
            name="mode",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_id",
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="recomendation_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterModelTable(
            name="product",
            table=None,
        ),
    ]
