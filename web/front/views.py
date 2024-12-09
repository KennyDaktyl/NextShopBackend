from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.articles.serializers import ArticlesListSerializer
from web.categories.serializers import CategoryListOnFirstPageSerializer
from web.front.serializers import ContactEmailSerializer, HeroSerializer
from web.functions import send_email_by_django
from web.models.articles import Article
from web.models.categories import Category
from web.models.heros import Hero


class FirstPageView(GenericAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve details of a first page",
    )
    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(
            is_active=True, on_first_page=True
        ).prefetch_related(
            Prefetch(
                "children",
                queryset=Category.objects.filter(is_active=True).order_by(
                    "order"
                ),
            )
        )
        heros = Hero.objects.filter(is_active=True)

        categories_serialized = CategoryListOnFirstPageSerializer(
            categories, many=True, context={"request": request}
        ).data
        heros_serialized = HeroSerializer(
            heros, many=True, context={"request": request}
        ).data

        articles = Article.objects.all().order_by("-created_date")[:3]
        articles_serialized = ArticlesListSerializer(
            articles, many=True, context={"request": request}
        ).data
        return Response(
            {"categories": categories_serialized, "heros": heros_serialized, "articles": articles_serialized},
            status=status.HTTP_200_OK,
        )


class ContactView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactEmailSerializer

    @swagger_auto_schema(
        operation_description="Retrieve contact details",
    )
    def get(self, request, *args, **kwargs):

        return Response(
            {"message": "Contact form"},
            status=status.HTTP_200_OK,
        )


class SendContactEmailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactEmailSerializer

    @swagger_auto_schema(
        operation_description="Retrieve contact details",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data.get("title")
            email = serializer.validated_data.get("email")
            message = serializer.validated_data.get("message")
            send_email_by_django(title, email, message)
            return Response(
                {"message": "Email sent successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


first_page_view = FirstPageView.as_view()
contact_view = ContactView.as_view()
senf_contact_email = SendContactEmailView.as_view()
