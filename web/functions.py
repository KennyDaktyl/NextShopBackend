import json

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def render_stamp_design_html(stamp_design):
    rows = "".join(
        f"<li>{line['text']} "
        f"(czcionka: {line['font']}, rozmiar: {line['size']}"
        f"{', pogrubienie' if line['bold'] else ''}"
        f"{', kursywa' if line['italic'] else ''})</li>"
        for line in stamp_design
    )
    return f"<p><strong>Projekt pieczątki:</strong></p><ol>{rows}</ol>"


def send_email_by_django(title, email, message, phone=None, stamp_design=None):
    subject, from_email, to = (
        title,
        settings.EMAIL_HOST_USER,
        settings.EMAIL_HOST_USER,
    )

    phone_html = f"<p>Telefon: <strong>{phone}</strong></p>" if phone else ""
    stamp_design_html = render_stamp_design_html(stamp_design) if stamp_design else ""

    html_content = f"""
    <html>
        <head></head>
        <body>
            <p>Message from: <h3>{email}</h3></p>
            {phone_html}
            <p>{message}</p>
            {stamp_design_html}
        </body>
    </html>
    """
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_key_photo_inquiry_email(inquiry):
    subject = "Nowe zgłoszenie: zdjęcie klucza do oceny"
    from_email = settings.EMAIL_HOST_USER
    to = settings.EMAIL_HOST_USER

    photo_url = ""
    if inquiry.photo:
        photo_url = f"{settings.SITE_URL.rstrip('/')}{settings.MEDIA_URL}{inquiry.photo.name}"

    note_html = f"<p><strong>Notatka:</strong> {inquiry.note}</p>" if inquiry.note else ""

    html_content = f"""
    <html>
        <head></head>
        <body>
            <p>Klient przesłał zdjęcie klucza do oceny.</p>
            <p>Email: <strong>{inquiry.email}</strong></p>
            <p>Telefon: <strong>{inquiry.phone}</strong></p>
            {note_html}
            <p><a href="{photo_url}">Zobacz zdjęcie klucza</a></p>
        </body>
    </html>
    """
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")

    if inquiry.photo:
        inquiry.photo.seek(0)
        msg.attach(
            inquiry.photo.name.split("/")[-1],
            inquiry.photo.read(),
            "application/octet-stream",
        )

    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending key photo inquiry email: {e}")
        return False


def send_activation_info_for_owner(title, message, user):
    send_email_by_django(title, settings.EMAIL_HOST_USER, message)
    return True


def send_email_order_status(order):
    subject = f"Zamówienie w Serwisie w Rybnej nr: {order.order_number} Zmiana statusu"
    from_email = settings.EMAIL_HOST_USER
    to = [
        settings.EMAIL_HOST_USER,
    ]

    if order.client and order.client.profile.send_emails:
        to.append(order.client_email)
    elif order.client is None:
        to.append(order.client_email)
    else:
        pass

    try:
        cart_items = json.loads(order.cart_items)
    except json.JSONDecodeError:
        cart_items = []

    html_content = render_to_string(
        "emails/order_status_email.html",
        {
            "order": order,
            "cart_items": cart_items,
        },
    )

    for email in to:
        msg = EmailMultiAlternatives(
            subject, html_content, from_email, [email]
        )
        msg.attach_alternative(html_content, "text/html")

        if hasattr(order, "invoice") and order.invoice.pdf:
            order.invoice.pdf.seek(0)
            msg.attach(
                f"faktura-{order.order_number}.pdf",
                order.invoice.pdf.read(),
                "application/pdf",
            )

        msg.send()
