# Generated by Django 5.0.6 on 2024-08-08 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0052_rename_image_category_oryg_image_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="thumbnail",
            old_name="org_oryg_image",
            new_name="oryg_image",
        ),
    ]
