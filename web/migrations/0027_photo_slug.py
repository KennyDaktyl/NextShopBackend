# Generated by Django 5.0.6 on 2024-07-01 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0026_photo_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
    ]