# Generated by Django 5.0.6 on 2024-08-28 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0075_alter_order_discount"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="client_phone",
            new_name="client_mobile",
        ),
    ]