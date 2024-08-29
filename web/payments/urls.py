from django.urls import path

from .views import payment_methods, webhook

urlpatterns = [
    path("payment-methods", payment_methods, name="payment-methods"),
    path("webhook", webhook, name="webhook"),
]
