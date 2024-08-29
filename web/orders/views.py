from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    GenericAPIView
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from web.models.deliveries import Delivery
from web.models.orders import Order, OrderItem
from web.models.payments import Payment

from .serializers import (
    CreateOrderSerializer,
    OrderSerializer,
    OrderUpdateStatusSerializer
)


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(client=user)


class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


class CreateOrderView(GenericAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        delivery_method_id = request.data.get('delivery_method')
        payment_method_id = request.data.get('payment_method')
        
        order_serializer = self.get_serializer(data=request.data)
        
        if order_serializer.is_valid():
            if delivery_method_id:
                delivery_method = get_object_or_404(Delivery, pk=delivery_method_id)
                order_serializer.validated_data['delivery_method'] = delivery_method

            if payment_method_id:
                payment_method = get_object_or_404(Payment, pk=payment_method_id)
                order_serializer.validated_data['payment_method'] = payment_method 
            
            order_serializer.validated_data['cart_items'] = json.dumps(request.data['cart_items'])
            
            if request.user.is_authenticated:
                order_serializer.validated_data['client'] = request.user
                
            order = Order.objects.create(
                **order_serializer.validated_data,
            )
            return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)
        else:
            print(order_serializer.errors)
            return Response({"errors": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class OrderDetailsView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(client=user)
        else:
            return Order.objects.none()


class UpdateOrderStatus(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        
        if not order_id:
            return Response({"detail": "Order ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        checkout_session_id = request.data.get('checkout_session_id')
        
        if new_status is None:
            return Response({"detail": "Status not provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if checkout_session_id:
            instance.checkout_session_id = checkout_session_id
            instance.save()

        instance.status = new_status
        instance.save()

        return Response({"detail": "Order status updated successfully."}, status=status.HTTP_200_OK)

