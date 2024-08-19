from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models.payments import Payment

from .serializers import PaymentMethodsSerializer


class PaymentMethodsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PaymentMethodsSerializer

    @swagger_auto_schema(
        operation_description="Deliveries",
        responses={200: PaymentMethodsSerializer()},
    )
    def get(self, request, *args, **kwargs):
        payment_methods = Payment.objects.filter(is_active=True)
        serializer = self.get_serializer(payment_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


payment_methods = PaymentMethodsView.as_view()
