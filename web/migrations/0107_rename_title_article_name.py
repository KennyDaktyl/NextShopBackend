# Generated by Django 5.0.6 on 2024-09-12 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0106_article_description"),
    ]

    operations = [
        migrations.RenameField(
            model_name="article",
            old_name="title",
            new_name="name",
        ),
    ]
