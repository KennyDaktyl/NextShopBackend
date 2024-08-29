from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models.products import Product

from .serializers import (ProductDetailsSerializer, ProductListItemSerializer,
                          ProductsPathListSerializer)


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListItemSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products",
        responses={200: ProductListItemSerializer(many=True)},
    )
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        search_query = self.request.query_params.get("search", None)
        if search_query:
            search_terms = search_query.split()
            query = Q()
            for term in search_terms:
                query &= Q(name__icontains=term) | Q(
                    description__icontains=term
                )
            queryset = queryset.filter(query)
        return queryset


class ProductsPathListView(generics.ListAPIView):
    serializer_class = ProductsPathListSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True)

    @swagger_auto_schema(
        operation_description="Retrieve a list of active product paths",
        responses={200: ProductsPathListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailsView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailsSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    @swagger_auto_schema(
        operation_description="Retrieve details of a product",
        responses={200: ProductDetailsSerializer()},
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


products_paths_list = ProductsPathListView.as_view()
