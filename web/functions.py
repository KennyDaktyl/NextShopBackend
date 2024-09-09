import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from web.models.orders import Invoice


def send_email_by_django(title, email, message):
    subject, from_email, to = (
        title,
        settings.EMAIL_HOST_USER,
        settings.EMAIL_HOST_USER,
    )

    html_content = f"""
    <html>
        <head></head>
        <body>
            <p>Message from: <h3>{email}</h3></p>
            <p>{message}</p>
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


def send_activation_info_for_owner(title, message, user):
    send_email_by_django(title, settings.EMAIL_HOST_USER , message)
    return True


def send_email_order_status(order):
    subject = f"Zamówienie w Serwisie w Rybnej nr: {order.order_number} zakończono pomyślnie."
    from_email = settings.EMAIL_HOST_USER
    to = [order.client_email, settings.EMAIL_HOST_USER,]

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
        msg = EmailMultiAlternatives(subject, html_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")

        if hasattr(order, 'invoice') and order.invoice.pdf:
            order.invoice.pdf.seek(0)
            msg.attach(
                f"faktura-{order.order_number}.pdf",
                order.invoice.pdf.read(),
                "application/pdf"
            )

        msg.send()
