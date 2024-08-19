from django.urls import path

from .views import payment_methods

urlpatterns = [
    path("payment-methods", payment_methods, name="payment-methods"),
]
