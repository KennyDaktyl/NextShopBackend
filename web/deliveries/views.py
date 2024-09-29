from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.carts.cart import Cart
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
        deliveries = Delivery.objects.filter(is_active=True)
        serializer = self.get_serializer(deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


delivery_methods = DeliveriesView.as_view()
