from django.urls import path

from .views import contact_form_email, first_page_view

urlpatterns = [
    path("first-page", first_page_view, name="first-page"),
    path("contact-email", contact_form_email, name="contact"),
]
