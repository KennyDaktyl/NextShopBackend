# Generated by Django 5.0.6 on 2024-08-29 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0077_payment_payment_online_alter_order_info"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="payment_id",
            new_name="checkout_session_id",
        ),
        migrations.RemoveField(
            model_name="order",
            name="order_code_stripe",
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
                    (4, "Do zapłaty"),
                    (5, "Płatność nieudana"),
                    (6, "Błąd płatności Stripe"),
                    (7, "W trakcie realizacji"),
                    (8, "W dostawie"),
                    (9, "Dostarczone"),
                    (10, "Zwrócone"),
                    (11, "Gotowe do odbioru"),
                    (12, "Zrealizowane"),
                    (13, "Anulowane"),
                ],
                default=0,
                verbose_name="Status",
            ),
        ),
    ]
