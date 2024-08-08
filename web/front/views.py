from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.categories.serializers import CategoryListOnFirstPageSerializer
from web.front.serializers import HeroSerializer
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
        )
        heros = Hero.objects.filter(is_active=True)
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


first_page_view = FirstPageView.as_view()
