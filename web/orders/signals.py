from django.db.models.signals import post_save
from django.dispatch import receiver

from web.models.orders import Invoice, Order
from web.utils import generate_invoice_for_order

STATUS_TO_MAKE_INVOICE = [3, 5, 8, 9, 12, 13]


@receiver(post_save, sender=Order)
def create_invoice(sender, instance, created, **kwargs):
    if (
        instance.make_invoice
        and not instance.invoice_created
        and instance.status in STATUS_TO_MAKE_INVOICE
    ):
        generate_invoice_for_order(instance)
        instance.invoice_created = True
        instance.save(update_fields=["invoice_created"])
