# Generated by Django 5.0.6 on 2024-07-01 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0028_alter_thumbnail_options_thumbnail_alt_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="thumbnail",
            name="height_expected",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Wysokość"
            ),
        ),
        migrations.AddField(
            model_name="thumbnail",
            name="width_expected",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Szerokość"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True, upload_to="products", verbose_name="Zdjęcie główne"
            ),
        ),
    ]
