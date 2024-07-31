from django.urls import path

from .views import ProductDetailsView, ProductListView

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path(
        "<slug:slug>/",
        ProductDetailsView.as_view(),
        name="product-details",
    ),
]
