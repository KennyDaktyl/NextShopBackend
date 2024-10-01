import uuid
from django.utils import timezone
import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from web.models.orders import Invoice


def generate_invoice_for_order(order, admin=False):
    current_month = timezone.now().strftime("%m")
    current_year = timezone.now().strftime("%Y")

    last_invoice = (
        Invoice.objects.filter(
            created_time__year=timezone.now().year,
            created_time__month=timezone.now().month,
        )
        .exclude(number__isnull=True)
        .first()
    )

    if admin:
        invoice_number = (
            order.invoice.override_number
            if order.invoice.override_number
            else order.invoice.number
        )
    else:
        if last_invoice:
            last_invoice_number = (
                last_invoice.override_number or last_invoice.number
            )
            try:
                last_number = int(last_invoice_number.split("-")[1])
            except (IndexError, ValueError) as e:
                last_number = 0
            next_number = str(last_number + 1).zfill(5)
        else:
            next_number = "00001"

        invoice_number = (
            f"faktura-{next_number}-{current_month}-{current_year}"
        )

    invoice, created = Invoice.objects.get_or_create(order=order)

    if not invoice.override_number:
        invoice.number = invoice_number
    else:
        invoice_number = invoice.override_number

    invoice_date = invoice.override_date or timezone.now().date()

    unique_uuid = uuid.uuid4()

    pdf_filename = f"invoices/{invoice_number}-{unique_uuid}.pdf"
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

    invoice.pdf = pdf_filename
    invoice.save()

    return invoice
