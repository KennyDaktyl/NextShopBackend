# Generated by Django 5.0.6 on 2024-07-02 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "web",
            "0029_thumbnail_height_expected_thumbnail_width_expected_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="categories",
                verbose_name="Zdjęcie kategorii",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="thumbnails",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
