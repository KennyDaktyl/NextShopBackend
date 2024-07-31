from django.urls import path

from web.categories.views import (
    CategoryMetaDataView,
    MenuItemsView,
    ProductsByCategorySlugView,
)

urlpatterns = [
    path(
        "menu-items/<slug:slug>/",
        MenuItemsView.as_view(),
        name="menu-items",
    ),
    path(
        "category-products/<slug:slug>/",
        ProductsByCategorySlugView.as_view(),
        name="products-by-category",
    ),
    path(
        "category-meta/<slug:slug>/",
        CategoryMetaDataView.as_view(),
        name="category-meta",
    ),
]
