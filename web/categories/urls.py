from django.urls import path

from web.categories.views import (CategoryMetaDataView, MenuItemsView,
                                  ProductsByCategorySlugView,
                                  categories_path_list)

urlpatterns = [
    path(
        "menu-items/<slug:slug>/",
        MenuItemsView.as_view(),
        name="menu-items",
    ),
    path(
        "categories-path-list/",
        categories_path_list,
        name="categories-list-path",
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
