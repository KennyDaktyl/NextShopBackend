# Generated by Django 5.0.6 on 2024-09-06 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0092_remove_cartitem_cart_remove_cartitem_product_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="nip",
            field=models.CharField(
                blank=True, max_length=12, null=True, verbose_name="NIP"
            ),
        ),
    ]