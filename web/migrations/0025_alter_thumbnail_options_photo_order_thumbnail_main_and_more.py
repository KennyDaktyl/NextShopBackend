# Generated by Django 5.0.6 on 2024-07-01 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0024_remove_thumbnail_size"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="thumbnail",
            options={
                "ordering": ["main", "order", "id"],
                "verbose_name": "Miniatura",
                "verbose_name_plural": "Miniatury",
            },
        ),
        migrations.AddField(
            model_name="photo",
            name="order",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="thumbnail",
            name="main",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="thumbnail",
            name="order",
            field=models.IntegerField(default=1),
        ),
    ]