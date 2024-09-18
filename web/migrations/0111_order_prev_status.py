# Generated by Django 5.0.6 on 2024-09-18 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0110_rename_modyfied_date_article_modified_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="prev_status",
            field=models.IntegerField(
                choices=[
                    (0, "Nowe"),
                    (1, "W trakcie płatności"),
                    (2, "Płatności anulowana"),
                    (3, "Opłacone"),
                    (4, "Płatność trwa weryfikacja"),
                    (5, "Do zapłaty"),
                    (6, "Płatność nieudana"),
                    (7, "Błąd płatności Stripe"),
                    (8, "W trakcie realizacji"),
                    (9, "W dostawie"),
                    (10, "Dostarczone"),
                    (11, "Zwrócone"),
                    (12, "Gotowe do odbioru"),
                    (13, "Zrealizowane"),
                    (14, "Anulowane"),
                ],
                default=0,
                verbose_name="Poprzedni status",
            ),
        ),
    ]
