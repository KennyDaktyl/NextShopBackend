from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from web.models.products import Product

from .serializers import ProductSerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products",
        responses={200: ProductSerializer(many=True)},
    )
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        return queryset

    def get(self, request, *args, **kwargs):
        print(request.headers)
        return super().get(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    @swagger_auto_schema(
        operation_description="Retrieve details of a product",
        responses={200: ProductSerializer()},
    )
    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(
                slug=self.kwargs["slug"]
            )
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

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products by category slug",
        responses={200: ProductSerializer(many=True)},
    )
    def get_queryset(self):
        queryset = Product.objects.filter(
            category__slug=self.kwargs["slug"], is_active=True
        )
        return queryset

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    