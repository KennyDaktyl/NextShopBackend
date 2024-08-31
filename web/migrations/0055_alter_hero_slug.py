# Generated by Django 5.0.6 on 2024-08-08 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0054_hero_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hero",
            name="slug",
            field=models.SlugField(
                blank=True, max_length=100, null=True, verbose_name="Slug"
            ),
        ),
    ]