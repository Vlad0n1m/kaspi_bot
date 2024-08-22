# Generated by Django 5.1 on 2024-08-22 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("product_id", models.CharField(max_length=255, unique=True)),
                ("default_url", models.TextField()),
                ("admin_url", models.TextField()),
                ("in_stock", models.CharField(max_length=50)),
                ("price", models.IntegerField()),
                ("list_position", models.IntegerField(blank=True, null=True)),
                ("best_price", models.IntegerField(blank=True, null=True)),
                ("min_price", models.IntegerField(blank=True, null=True)),
                ("recomendation_price", models.IntegerField(blank=True, null=True)),
                (
                    "concurents",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("mode", models.CharField(default="0", max_length=10)),
            ],
            options={
                "db_table": "products",
            },
        ),
    ]
