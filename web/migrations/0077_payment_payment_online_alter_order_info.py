# Generated by Django 5.0.6 on 2024-08-28 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0076_rename_client_phone_order_client_mobile"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="payment_online",
            field=models.BooleanField(
                default=False, verbose_name="Czy to płatność online?"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="info",
            field=models.TextField(
                blank=True, null=True, verbose_name="Informacje do zamówienia"
            ),
        ),
    ]
