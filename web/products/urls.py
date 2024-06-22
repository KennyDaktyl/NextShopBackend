from django.urls import path

from .views import ProductDetailView, ProductListView, ProductsByCategorySlugView

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path(
        "category/<slug:slug>/",
        ProductsByCategorySlugView.as_view(),
        name="products-by-category",
    ),
    path(
        "<slug:category_slug>/<slug:slug>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]
