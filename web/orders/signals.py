from django.db.models.signals import post_save
from django.dispatch import receiver

from web.functions import send_email_order_status
from web.models.orders import Invoice, Order
from web.utils import generate_invoice_for_order

STATUS_TO_MAKE_INVOICE = [3, 5, 8, 9, 12, 13]


@receiver(post_save, sender=Order)
def oder_create_or_update_signals(sender, instance, created, **kwargs):
    if (
        instance.make_invoice
        and not instance.invoice_created
        and instance.status in STATUS_TO_MAKE_INVOICE
    ):
        generate_invoice_for_order(instance)
        instance.invoice_created = True
        instance.save(update_fields=["invoice_created"])

    if instance.client is not None:
        if not instance.client.profile.send_emails:
            return

    # if instance.status in [3, 5, 9, 12, 14] and instance.prev_status != instance.status:
    #     print("Sending email", instance.status, instance.prev_status)
    #     send_email_order_status(instance)
