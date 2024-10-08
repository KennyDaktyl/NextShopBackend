# Generated by Django 5.0.6 on 2024-08-19 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0065_thumbnail_payment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="delivery",
            options={
                "ordering": ["order", "name"],
                "verbose_name": "Rodzaj dostawy",
                "verbose_name_plural": "Rodzaje dostawy",
            },
        ),
        migrations.AlterModelOptions(
            name="payment",
            options={
                "ordering": ["order", "name"],
                "verbose_name": "Rodzaj płatności",
                "verbose_name_plural": "Rodzaje płatności",
            },
        ),
        migrations.RemoveField(
            model_name="payment",
            name="is_online",
        ),
        migrations.AddField(
            model_name="payment",
            name="online_payment_upon_delivery",
            field=models.BooleanField(
                default=False,
                verbose_name="Czy to płatność online przy odbiorze?",
            ),
        ),
    ]
