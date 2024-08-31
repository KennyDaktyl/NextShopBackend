# Generated by Django 5.0.6 on 2024-08-06 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0045_alter_productoption_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="product_options",
        ),
        migrations.AddField(
            model_name="product",
            name="product_option",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="web.productoption",
            ),
        ),
    ]