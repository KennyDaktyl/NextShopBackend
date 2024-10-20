from django.conf import settings
from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.carts.cart import Cart
from web.models.products import Product

from .serializers import (
    ProductDetailsSerializer,
    ProductGoogleMerchantSerializer,
    ProductListItemSerializer,
    ProductReviewSerializer,
    ProductsPathListSerializer,
)


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
            cart = Cart(request)
            product = Product.objects.get(slug=self.kwargs["slug"])
            product.free_delivery_threshold = settings.FREE_DELIVERY_THRESHOLD
            product.free_delivery_threshold_passed = cart.is_free_delivery()
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProductFeedXMLView(TemplateView):
    template_name = "products/feed_google.xml"  # Ścieżka do Twojego szablonu XML

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        products = Product.objects.filter(is_active=True, is_service=False)
        serializer = ProductGoogleMerchantSerializer(products, many=True, context={'request': self.request})
        context['products'] = serializer.data
        context['channel_title'] = 'Dorabianie Kluczy i Wyrób Pieczątek - Serwis w Rybnej | Naprawa Telefonów'
        context['channel_link'] = "https://serwiswrybnej.pl"
        context['channel_description'] = 'Feed produktów w sklepie Serwis w Rybnej'
        
        return context


class ProductReviewCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=None)
            return Response({"message": "Review sent successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

products_paths_list = ProductsPathListView.as_view()
products_feed_xml = ProductFeedXMLView.as_view()
add_review = ProductReviewCreateView.as_view()
