from django.urls import path

from .views import contact_view, first_page_view, senf_contact_email

urlpatterns = [
    path("first-page", first_page_view, name="first-page"),
    path("contact", contact_view, name="contact"),
    path("contact-email", senf_contact_email, name="contact"),
]
