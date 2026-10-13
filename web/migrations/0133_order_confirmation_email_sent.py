from django.db import migrations, models


def mark_existing_orders_as_confirmed(apps, schema_editor):
    # Istniejące zamówienia są już obsłużone - nie wysyłamy im zaległych
    # potwierdzeń przy najbliższej zmianie statusu.
    Order = apps.get_model("web", "Order")
    Order.objects.update(confirmation_email_sent=True)


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0132_order_items_from_cart_items"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="confirmation_email_sent",
            field=models.BooleanField(
                default=False,
                verbose_name="Wysłano e-mail z potwierdzeniem zamówienia",
            ),
        ),
        migrations.RunPython(
            mark_existing_orders_as_confirmed, migrations.RunPython.noop
        ),
    ]
