# Generated by Django 5.0.6 on 2024-08-21 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0067_remove_payment_online_payment_upon_delivery_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hero",
            name="link_text",
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name="Tekst linku",
            ),
        ),
    ]
