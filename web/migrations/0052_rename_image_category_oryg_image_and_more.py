# Generated by Django 5.0.6 on 2024-08-08 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0051_thumbnail_hero"),
    ]

    operations = [
        migrations.RenameField(
            model_name="category",
            old_name="image",
            new_name="oryg_image",
        ),
        migrations.RenameField(
            model_name="hero",
            old_name="image",
            new_name="oryg_image",
        ),
        migrations.RenameField(
            model_name="photo",
            old_name="image",
            new_name="oryg_image",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="image",
            new_name="oryg_image",
        ),
        migrations.RenameField(
            model_name="productvariant",
            old_name="image",
            new_name="oryg_image",
        ),
        migrations.RenameField(
            model_name="thumbnail",
            old_name="image",
            new_name="org_oryg_image",
        ),
    ]