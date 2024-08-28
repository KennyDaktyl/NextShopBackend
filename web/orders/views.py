from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
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
    OrderItemSerializer
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


class AddOrderItems(CreateAPIView):
    serializer_class = OrderItemSerializer

    def post(self, request, *args, **kwargs):
        try:
            order_id = kwargs.get("order_id")
            order = Order.objects.get(pk=order_id)

            if isinstance(request.data, list):
                serializer = self.get_serializer(data=request.data, many=True)
            else:
                serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)

            order_items = []
            for item_data in serializer.validated_data:
                item_data["order"] = order
                order_items.append(OrderItem(**item_data))

            OrderItem.objects.bulk_create(order_items)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response(
                {"message": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UpdateOrderItem(UpdateAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteOrderItem(DestroyAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, order_id=self.kwargs.get("pk"))
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
