# Generated by Django 5.0.6 on 2024-08-08 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0048_remove_category_main_category_on_first_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="on_first_page",
            field=models.BooleanField(
                default=False, verbose_name="Na 1 stronie?"
            ),
        ),
    ]
