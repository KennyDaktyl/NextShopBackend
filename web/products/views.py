from rest_framework import generics, status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from web.models.products import Product
from .serializers import ProductSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of active products",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description="Retrieve details of a product",
        responses={200: ProductSerializer()}
    )

    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(pk=self.kwargs['pk'], slug=self.kwargs['slug'])
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)