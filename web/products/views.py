from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models.categories import Category
from web.models.products import Product

from .serializers import CategorySerializer, ProductSerializer


class ProductPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products",
        responses={200: ProductSerializer(many=True)},
    )
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        return queryset


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
        category_data = CategorySerializer(category).data
        subcategories_data = CategorySerializer(subcategories, many=True).data
        custom_response = {
            "name": category_data["name"],
            "slug": category_data["slug"],
            "back_link": category_data["back_link"],
            "items": subcategories_data,
        }
        return Response(custom_response)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    @swagger_auto_schema(
        operation_description="Retrieve details of a product",
        responses={200: ProductSerializer()},
    )
    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(slug=self.kwargs["slug"])
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProductsByCategorySlugView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products by category slug",
        responses={200: ProductSerializer(many=True)},
    )
    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs["slug"], is_active=True
        )

        if category.has_children:
            descendants = category.get_descendants()
            all_categories = [category] + list(descendants)
        else:
            all_categories = [category]

        queryset = Product.objects.filter(
            category__in=all_categories, is_active=True
        )
        return queryset
