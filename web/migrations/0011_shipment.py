# Generated by Django 4.2.13 on 2024-05-15 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0010_alter_cart_created_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Shipment",
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
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Nazwa"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Cena"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, verbose_name="Czy aktywna"
                    ),
                ),
            ],
            options={
                "verbose_name": "Rodzaj dostawy",
                "verbose_name_plural": "Rodzaj dostawy",
                "ordering": ["name"],
            },
        ),
    ]