# Generated by Django 5.0.6 on 2024-06-16 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "web",
            "0015_alter_productprice_product_alter_profile_price_group_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True, upload_to="products", verbose_name="verobse_name"
            ),
        ),
    ]