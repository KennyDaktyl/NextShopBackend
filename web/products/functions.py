from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_order_details_email(subject, order):
    subject, from_email, to = (
        subject,
        settings.EMAIL_HOST_USER,
        order.client_email,
    )

    html_content = render_to_string(
        "emails/order_status_email.html",
        {
            "order": order,
        },
    )

    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")

    if hasattr(order, "invoice") and order.invoice.pdf:
        with open(order.invoice.pdf.path, "rb") as pdf_file:
            msg.attach(
                f"faktura_{order.invoice.number}.pdf",
                pdf_file.read(),
                "application/pdf",
            )

    msg.send()
