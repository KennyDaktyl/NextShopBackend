from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models.categories import Category
from web.models.products import Product
from web.products.serializers import ProductListItemSerializer
from web.products.views import ProductPagination

from .serializers import (
    CategoryMetaDataSerializer,
    CategoryPathSerializer,
    CategorySerializer,
    ProductsByCategorySerializer,
)


class MenuItemsView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products for a sub menu",
        responses={200: CategorySerializer(many=True)},
    )
    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_object(self):
        slug = self.kwargs["slug"]
        category = get_object_or_404(Category, slug=slug, is_active=True)
        return category

    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        subcategories = Category.objects.filter(
            parent=category, is_active=True
        )
        context = {"request": request}
        category_data = CategorySerializer(category, context=context).data
        subcategories_data = CategorySerializer(
            subcategories, many=True, context=context
        ).data
        custom_response = {
            "name": category_data["name"],
            "slug": category_data["slug"],
            "description": category_data["description"],
            "seo_text": category_data["seo_text"],
            "back_link": category_data["back_link"],
            "has_children": category_data["has_children"],
            "full_path": category_data["full_path"],
            "image": category_data["image"],
            "items": subcategories_data,
        }
        return Response(custom_response)


class CategoriesPathListView(generics.ListAPIView):
    serializer_class = CategoryPathSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of active categories",
        responses={200: CategorySerializer(many=True)},
    )
    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        context = {"request": request}
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)


class CategoryMetaDataView(generics.RetrieveAPIView):
    serializer_class = CategoryMetaDataSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @swagger_auto_schema(
        operation_description="Retrieve details of a category",
        responses={200: CategoryMetaDataSerializer()},
    )
    def get_object(self):
        slug = self.kwargs["slug"]
        category = get_object_or_404(Category, slug=slug, is_active=True)
        return category

    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        category_data = self.serializer_class(category).data
        return Response(category_data)


class ProductsByCategorySlugView(generics.ListAPIView):
    serializer_class = ProductListItemSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products by category slug",
        responses={200: ProductListItemSerializer(many=True)},
    )
    def get_queryset(self):
        slug = self.kwargs["slug"]
        category = get_object_or_404(Category, slug=slug, is_active=True)

        if category.has_children:
            descendants = category.get_descendants()
            all_categories = [category] + list(descendants)
        else:
            all_categories = [category]

        products = Product.objects.filter(
            category__in=all_categories, is_active=True
        )
        return products

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        category = get_object_or_404(
            Category, slug=self.kwargs["slug"], is_active=True
        )

        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            paginated_response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(
                queryset, many=True, context={"request": request}
            )
            paginated_response = {
                "count": len(queryset),
                "next": None,
                "previous": None,
                "results": serializer.data,
            }

        paginated_response.data["category"] = ProductsByCategorySerializer(
            category
        ).data
        return Response(paginated_response.data)


categories_path_list = CategoriesPathListView.as_view()
