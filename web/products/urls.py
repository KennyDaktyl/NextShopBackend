from django.urls import path

from .views import ProductDetailsView, ProductListView, products_paths_list

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path(
        "products-list-path/",
        products_paths_list,
        name="products-paths-list",
    ),
    path(
        "<slug:slug>/",
        ProductDetailsView.as_view(),
        name="product-details",
    ),
]
