from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from web.constants import STATUS_FOR_SEND_EMAIL
from web.functions import send_email_order_status
from web.models.orders import Invoice, Order, OrderItem
from web.utils import generate_invoice_for_order

STATUS_TO_MAKE_INVOICE = [3, 5, 8, 9, 12, 13]


def send_status_changed_email(order_pk):
    # Błąd wysyłki nie może blokować zapisu zamówienia (admin, webhook
    # Stripe) - inaczej Stripe ponawia webhook i klient dostaje duplikaty.
    try:
        order = Order.objects.get(pk=order_pk)
        send_email_order_status(order, status_changed=True)
    except Exception as e:
        print(f"Error sending order status email for order {order_pk}: {e}")


@receiver(post_save, sender=Order)
def oder_create_or_update_signals(sender, instance, created, **kwargs):
    # Flagi z Order.save() trzeba odczytać przed generowaniem faktury -
    # instance.save(update_fields=...) poniżej je resetuje.
    is_status_changed = getattr(instance, "is_status_changed", False)
    is_paid_changed = getattr(instance, "is_paid_changed", False)
    is_totals_changed = getattr(instance, "is_totals_changed", False)

    if (
        instance.make_invoice
        and not instance.invoice_created
        and instance.status in STATUS_TO_MAKE_INVOICE
    ):
        generate_invoice_for_order(instance)
        instance.invoice_created = True
        instance.save(update_fields=["invoice_created"])
    elif (
        instance.make_invoice
        and instance.invoice_created
        and (is_paid_changed or is_totals_changed)
    ):
        # Status "Opłacone" lub kwoty (np. rabat) zmieniły się po tym, jak
        # faktura została już wystawiona - przerenderowujemy PDF z tym
        # samym numerem.
        generate_invoice_for_order(instance)

    if (
        is_status_changed
        and instance.status in STATUS_FOR_SEND_EMAIL
        and instance.email_notification
        and not instance.delivery_method.in_store_pickup
    ):
        order_pk = instance.pk
        transaction.on_commit(lambda: send_status_changed_email(order_pk))


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def order_item_changed(sender, instance, **kwargs):
    # Zapis przez update() - bez ponownego wywołania sygnałów Order.
    order = Order.objects.filter(pk=instance.order_id).first()
    if order is not None:
        order.update_totals()
