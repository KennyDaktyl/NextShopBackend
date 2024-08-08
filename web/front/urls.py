from django.urls import path

from .views import first_page_view

urlpatterns = [
    path("first-page", first_page_view, name="first-page"),
]
