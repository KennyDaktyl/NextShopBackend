# Generated by Django 5.0.6 on 2024-09-03 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0088_rename_invoice_profile_make_invoice"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_service",
            field=models.BooleanField(default=False, verbose_name="Usługa"),
        ),
    ]
