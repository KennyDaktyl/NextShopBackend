import base64
import json

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

ALIGN_LABELS = {
    "left": "do lewej",
    "center": "do środka",
    "right": "do prawej",
}

COLOR_LABELS = {
    "black": "czarny",
    "red": "czerwony",
    "green": "zielony",
    "blue": "niebieski",
}


def render_stamp_design_html(stamp_design):
    rows = "".join(
        f"<li>{line['text']} "
        f"(czcionka: {line['font']}, rozmiar: {line['size']}"
        f"{', pogrubienie' if line['bold'] else ''}"
        f"{', kursywa' if line['italic'] else ''}"
        ", wyrównanie: "
        f"{ALIGN_LABELS.get(line.get('align', 'center'), 'do środka')})</li>"
        for line in stamp_design
    )
    return f"<p><strong>Projekt pieczątki:</strong></p><ol>{rows}</ol>"


def send_email_by_django(
    title,
    email,
    message,
    phone=None,
    stamp_design=None,
    stamp_image=None,
    stamp_color=None,
):
    subject, from_email, to = (
        title,
        settings.EMAIL_HOST_USER,
        settings.EMAIL_HOST_USER,
    )

    phone_html = f"<p>Telefon: <strong>{phone}</strong></p>" if phone else ""
    stamp_design_html = render_stamp_design_html(stamp_design) if stamp_design else ""
    stamp_color_html = (
        f"<p>Kolor tuszu: <strong>{COLOR_LABELS.get(stamp_color, stamp_color)}</strong></p>"
        if stamp_color
        else ""
    )

    html_content = f"""
    <html>
        <head></head>
        <body>
            <p>Message from: <h3>{email}</h3></p>
            {phone_html}
            <p>{message}</p>
            {stamp_color_html}
            {stamp_design_html}
        </body>
    </html>
    """
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")

    if stamp_image:
        try:
            image_bytes = base64.b64decode(stamp_image)
            msg.attach("projekt-pieczatki.jpg", image_bytes, "image/jpeg")
        except (ValueError, TypeError) as e:
            print(f"Error attaching stamp image: {e}")

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


def _order_email_subjects(order, status_changed, confirmation):
    """Zwraca (temat dla klienta, temat dla sklepu)."""
    if confirmation:
        client_subject = (
            f"Potwierdzenie zamówienia nr {order.order_number} - Serwis w Rybnej"
        )
        shop_subject = (
            f"Nowe zamówienie nr {order.order_number}: {order.amount} zł, "
            f"{order.payment_method.name}, {order.delivery_method.name} "
            f"({order.get_status_display()})"
        )
        return client_subject, shop_subject
    if status_changed:
        subject = (
            f"Zmieniono status zamówienia nr {order.order_number} "
            f"na: {order.get_status_display()} - Serwis w Rybnej"
        )
    else:
        subject = f"Zamówienie w Serwisie w Rybnej nr: {order.order_number} Zmiana statusu"
    return subject, subject


def send_email_order_status(order, status_changed=False, confirmation=False):
    """Wysyła e-mail o zamówieniu do sklepu i (jeśli włączone) do klienta.

    Każdy odbiorca jest wysyłany osobno - błąd wysyłki do jednego nie
    blokuje drugiego. Zwraca liczbę wysłanych wiadomości.
    """
    client_subject, shop_subject = _order_email_subjects(
        order, status_changed, confirmation
    )
    from_email = settings.EMAIL_HOST_USER
    recipients = [(settings.EMAIL_HOST_USER, shop_subject)]
    # E-maile o zamówieniu są transakcyjne - o wysyłce do klienta decyduje
    # przełącznik na zamówieniu, nie zgoda na maile w profilu.
    if order.email_notification and order.client_email:
        recipients.append((order.client_email, client_subject))

    try:
        cart_items = json.loads(order.cart_items)
    except (json.JSONDecodeError, TypeError):
        cart_items = []

    html_content = render_to_string(
        "emails/order_status_email.html",
        {
            "order": order,
            "cart_items": cart_items,
            "order_items": [
                item
                for item in order.order_items.all()
                if item.item_type == item.TYPE_PRODUCT
            ],
            "status_changed": status_changed and not confirmation,
        },
    )
    text_content = strip_tags(html_content)

    sent = 0
    for email, subject in recipients:
        try:
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [email]
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
            sent += 1
        except Exception as e:
            print(
                f"Error sending order email ({order.order_number}) "
                f"to {email}: {e}"
            )
    return sent
