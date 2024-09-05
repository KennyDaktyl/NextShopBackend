from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Prefetch

from web.categories.serializers import CategoryListOnFirstPageSerializer
from web.front.serializers import ContactEmailSerializer, HeroSerializer
from web.functions import send_email_by_django
from web.models.categories import Category
from web.models.heros import Hero


class FirstPageView(GenericAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve details of a first page",
    )
    def get(self, request, *args, **kwargs):
        # Pobieranie kategorii z posortowanymi podkategoriami
        categories = Category.objects.filter(
            is_active=True, on_first_page=True
        ).prefetch_related(
            Prefetch(
                'children',  # Nazwa relacji (related_name)
                queryset=Category.objects.filter(is_active=True).order_by('order')  # Sortowanie po 'order'
            )
        )

        # Pobieranie aktywnych herosów
        heros = Hero.objects.filter(is_active=True)

        # Serializacja kategorii i herosów
        categories_serialized = CategoryListOnFirstPageSerializer(
            categories, many=True, context={"request": request}
        ).data
        heros_serialized = HeroSerializer(
            heros, many=True, context={"request": request}
        ).data

        return Response(
            {"categories": categories_serialized, "heros": heros_serialized},
            status=status.HTTP_200_OK,
        )
        

class ContactView(GenericAPIView):
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
contact_form_email = ContactView.as_view()
