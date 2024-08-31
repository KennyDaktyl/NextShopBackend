# Generated by Django 5.0.6 on 2024-08-27 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0073_alter_order_amount_with_discount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="amount_with_discount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Cena z rabatem",
            ),
        ),
    ]