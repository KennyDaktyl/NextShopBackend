from django.urls import path

from .views import delivery_methods

urlpatterns = [
    path("delivery-methods", delivery_methods, name="delivery-methods"),
]
