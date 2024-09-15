from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.articles.serializers import (ArticlesDetailsSerializer,
                                      ArticlesListSerializer,
                                      ArticlesPathListSerializer)
from web.models.articles import Article


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ArticlesListView(generics.ListAPIView):
    serializer_class = ArticlesListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    @swagger_auto_schema(
        operation_description="Retrieve a list of active articles",
        responses={200: ArticlesListSerializer(many=True)},
    )
    def get_queryset(self):
        queryset = Article.objects.all()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            search_terms = search_query.split()
            query = Q()
            for term in search_terms:
                query &= Q(title__icontains=term) | Q(
                    description__icontains=term
                )
            queryset = queryset.filter(query)
        return queryset


class ArticlesDetailsView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticlesDetailsSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    @swagger_auto_schema(
        operation_description="Retrieve a details of active article",
        responses={200: ArticlesDetailsSerializer},
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ArticlesPathListView(generics.ListAPIView):
    serializer_class = ArticlesPathListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of active articles path",
        responses={200: ArticlesPathListSerializer(many=True)},
    )
    def get_queryset(self):
        return Article.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        context = {"request": request}
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)
