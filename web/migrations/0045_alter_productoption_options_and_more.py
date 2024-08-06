# Generated by Django 5.0.6 on 2024-08-06 09:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0044_alter_productoption_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productoption",
            options={
                "verbose_name": "Opcja produktu",
                "verbose_name_plural": "Opcje produktu",
            },
        ),
        migrations.AlterModelOptions(
            name="productoptionitem",
            options={
                "ordering": ["order", "name"],
                "verbose_name": "Opcje element",
                "verbose_name_plural": "Opcje elementy",
            },
        ),
        migrations.RemoveField(
            model_name="productoption",
            name="order",
        ),
        migrations.AddField(
            model_name="productoptionitem",
            name="order",
            field=models.IntegerField(default=1, verbose_name="Kolejność"),
        ),
        migrations.AlterField(
            model_name="productoptionitem",
            name="feature",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="options",
                to="web.productoption",
                verbose_name="Opcja produktu",
            ),
        ),
    ]
