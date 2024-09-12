# Generated by Django 5.0.6 on 2024-09-12 10:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0102_alter_order_uid"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                    "title",
                    models.CharField(max_length=256, verbose_name="Tytuł"),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        max_length=256,
                        null=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data utworzenia"
                    ),
                ),
                (
                    "image_oryg",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="articles",
                        verbose_name="Zdjęcie",
                    ),
                ),
                (
                    "image_alt",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Tekst alternatywny",
                    ),
                ),
                (
                    "image_title",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Tytuł zdjęcia",
                    ),
                ),
                ("content", models.TextField(verbose_name="Treść")),
                (
                    "meta_description",
                    models.CharField(
                        blank=True,
                        max_length=160,
                        null=True,
                        verbose_name="Meta description dla artykułu",
                    ),
                ),
                (
                    "meta_title",
                    models.CharField(
                        blank=True,
                        max_length=60,
                        null=True,
                        verbose_name="Meta title dla artykułu",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="articles",
                        to="web.category",
                        verbose_name="Kategoria",
                    ),
                ),
                (
                    "prev_category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prev_articles",
                        to="web.category",
                        verbose_name="Poprzednia kategoria",
                    ),
                ),
            ],
            options={
                "verbose_name": "Artykuł",
                "verbose_name_plural": "Artykuły",
                "ordering": ["created_date"],
            },
        ),
    ]