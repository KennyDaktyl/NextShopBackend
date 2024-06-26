# Generated by Django 4.2.13 on 2024-05-15 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0004_alter_product_options_alter_product_slug_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(
                blank=True, null=True, verbose_name="Opis produktu"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(
                db_index=True, max_length=255, verbose_name="Nazwa"
            ),
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order",
                    models.IntegerField(default=1, verbose_name="Kolejność"),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, verbose_name="Nazwa kategorii"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        max_length=255,
                        null=True,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="Opis kategorii"
                    ),
                ),
                (
                    "is_menu",
                    models.BooleanField(
                        default=False, verbose_name="Czy w menu głównym"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, verbose_name="Czy aktywna"
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="web.category",
                        verbose_name="Kategoria rodzic",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Kategorie",
                "ordering": ("order", "name"),
            },
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="web.category",
                verbose_name="Kategoria",
            ),
            preserve_default=False,
        ),
    ]
