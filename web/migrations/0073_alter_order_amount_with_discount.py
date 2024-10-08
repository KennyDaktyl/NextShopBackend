# Generated by Django 5.0.6 on 2024-08-27 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0072_order_cart_items_order_cart_items_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="amount_with_discount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                verbose_name="Cena z rabatem",
            ),
        ),
    ]
