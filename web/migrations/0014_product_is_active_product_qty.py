# Generated by Django 4.2.13 on 2024-05-15 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0013_alter_order_created_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_active",
            field=models.BooleanField(
                default=True, verbose_name="Czy aktywny"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="qty",
            field=models.IntegerField(default=0, verbose_name="Ilość"),
        ),
    ]
