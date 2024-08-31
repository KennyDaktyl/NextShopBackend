# Generated by Django 5.0.6 on 2024-08-29 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0078_rename_payment_id_order_checkout_session_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="company_payer",
            field=models.TextField(
                blank=True, null=True, verbose_name="Dane Płatnika"
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="invoice",
            field=models.BooleanField(default=False, verbose_name="Faktura"),
        ),
        migrations.AddField(
            model_name="profile",
            name="invoice_city",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Miasto"
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="invoice_house_number",
            field=models.CharField(
                blank=True, max_length=10, null=True, verbose_name="Numer domu"
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="invoice_local_number",
            field=models.CharField(
                blank=True,
                max_length=10,
                null=True,
                verbose_name="Numer lokalu",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="invoice_postal_code",
            field=models.CharField(
                blank=True,
                max_length=6,
                null=True,
                verbose_name="Kod pocztowy",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="invoice_street",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Ulica"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
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
                verbose_name="Status",
            ),
        ),
    ]