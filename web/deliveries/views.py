from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.deliveries.serializers import DeliveriesSerializer
from web.models.deliveries import Delivery


class DeliveriesView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = DeliveriesSerializer

    @swagger_auto_schema(
        operation_description="Deliveries",
        responses={200: DeliveriesSerializer()},
    )
    def get(self, request, *args, **kwargs):
        delivery = Delivery.objects.filter(is_active=True)
        serializer = self.get_serializer(delivery, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


delivery_methods = DeliveriesView.as_view()
