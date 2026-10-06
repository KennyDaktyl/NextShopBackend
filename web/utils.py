import re
import uuid
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone
import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from web.models.orders import Invoice

# Dowolna stała - identyfikator blokady numeracji faktur w PostgreSQL.
INVOICE_NUMBER_LOCK_ID = 74210001


def _next_invoice_number(month, year):
    """Najwyższy numer faktury z danego miesiąca + 1.

    Liczone po numerach (również nadpisanych), a nie po created_time
    ostatniej faktury, żeby kolejność tworzenia nie wpływała na numerację.
    """
    pattern = re.compile(rf"^faktura-(\d+)-{month}-{year}$")
    suffix = f"-{month}-{year}"
    max_number = 0
    for number, override_number in Invoice.objects.filter(
        Q(number__endswith=suffix) | Q(override_number__endswith=suffix)
    ).values_list("number", "override_number"):
        for value in (number, override_number):
            match = pattern.match(value or "")
            if match:
                max_number = max(max_number, int(match.group(1)))
    return f"faktura-{str(max_number + 1).zfill(5)}-{month}-{year}"


def generate_invoice_for_order(order, admin=False):
    """Generuje PDF faktury dla zamówienia.

    Numer jest nadawany tylko raz - przy pierwszym wystawieniu. Każde
    kolejne wywołanie (zmiana opłacenia, akcja w adminie) przerenderowuje
    PDF z tym samym numerem i datą wystawienia.
    """
    with transaction.atomic():
        # Blokada do końca transakcji - dwa równoległe zamówienia nie
        # dostaną tego samego numeru.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_xact_lock(%s)", [INVOICE_NUMBER_LOCK_ID]
            )
        invoice, created = Invoice.objects.select_for_update().get_or_create(
            order=order
        )
        if not invoice.number:
            now = timezone.now()
            invoice.number = _next_invoice_number(
                now.strftime("%m"), now.strftime("%Y")
            )
            invoice.save(update_fields=["number"])

    invoice_number = invoice.override_number or invoice.number
    invoice_date = invoice.override_date or invoice.created_time.date()
    old_pdf_name = invoice.pdf.name if invoice.pdf else None

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

    if old_pdf_name and old_pdf_name != pdf_filename:
        old_pdf_path = os.path.join(settings.MEDIA_ROOT, old_pdf_name)
        if os.path.isfile(old_pdf_path):
            os.remove(old_pdf_path)

    invoice.pdf = pdf_filename
    invoice.save(update_fields=["pdf"])

    return invoice
