from django.urls import path

from .views import (MenuItemsView, ProductDetailView, ProductListView,
                    ProductsByCategorySlugView)

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path(
        "menu-items/<slug:slug>/",
        MenuItemsView.as_view(),
        name="menu-items",
    ),
    path(
        "category/<slug:slug>/",
        ProductsByCategorySlugView.as_view(),
        name="products-by-category",
    ),
    path(
        "<slug:slug>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]
