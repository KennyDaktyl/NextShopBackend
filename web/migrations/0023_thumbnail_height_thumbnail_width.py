# Generated by Django 5.0.6 on 2024-07-01 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0022_alter_photo_thumbnails"),
    ]

    operations = [
        migrations.AddField(
            model_name="thumbnail",
            name="height",
            field=models.IntegerField(default=1, verbose_name="Wysokość"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="thumbnail",
            name="width",
            field=models.IntegerField(default=1, verbose_name="Szerokość"),
            preserve_default=False,
        ),
    ]
