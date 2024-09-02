import os

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from web.models.orders import Invoice


def generate_invoice_for_order(order):
    invoice, created = Invoice.objects.get_or_create(order=order)

    invoice_number = invoice.override_number or f"faktura-{order.order_number}"
    invoice_date = invoice.override_date or timezone.now().date()

    pdf_filename = f"invoices/{invoice_number}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

    pdf_dir = os.path.dirname(pdf_path)
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    html_content = render_to_string(
        "emails/invoice.html",
        {
            "order": order,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
        },
    )
    html = HTML(string=html_content)
    html.write_pdf(target=pdf_path)

    invoice.number = invoice_number
    invoice.override_number = invoice.override_number
    invoice.override_date = invoice.override_date
    invoice.pdf = pdf_filename
    invoice.save()

    return invoice
