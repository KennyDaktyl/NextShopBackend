# Generated by Django 5.0.6 on 2024-10-01 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0112_alter_order_invoice_city_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="price_promo",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="Cena promocyjna",
            ),
        ),
    ]
