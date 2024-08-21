from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


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
