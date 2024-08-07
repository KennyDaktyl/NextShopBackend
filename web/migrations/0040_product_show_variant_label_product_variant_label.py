# Generated by Django 5.0.6 on 2024-07-25 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0039_productvariant_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="show_variant_label",
            field=models.BooleanField(
                default=False, verbose_name="Pokazuj etykietę wariantu"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="variant_label",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Etykieta wariantu",
            ),
        ),
    ]
