# Generated by Django 5.0.6 on 2024-07-25 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0040_product_show_variant_label_product_variant_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="tags",
            field=models.ManyToManyField(
                blank=True, to="web.tag", verbose_name="Tagi"
            ),
        ),
    ]