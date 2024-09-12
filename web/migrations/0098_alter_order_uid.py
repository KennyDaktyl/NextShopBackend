# Generated by Django 5.0.6 on 2024-09-09 14:50

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0097_alter_order_uid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="uid",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                null=True,
                verbose_name="Unikalny identyfikator",
            ),
        ),
    ]