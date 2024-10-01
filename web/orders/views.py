import json
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from web.carts.cart import Cart
from web.constants import STATUS_FOR_SEND_EMAIL
from web.functions import send_email_order_status
from web.models.deliveries import Delivery
from web.models.orders import Order
from web.models.payments import Payment

from .serializers import CreateOrderSerializer, OrderSerializer


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

        delivery_method_id = request.data.get("delivery_method")
        payment_method_id = request.data.get("payment_method")

        order_serializer = self.get_serializer(data=request.data)

        if order_serializer.is_valid():
            cart = Cart(request)

            if delivery_method_id:
                delivery_method = get_object_or_404(
                    Delivery, pk=delivery_method_id
                )

                is_free_delivery = cart.is_free_delivery() if cart else False
                if is_free_delivery:
                    delivery_method.price = delivery_method.price_promo

                order_serializer.validated_data["delivery_method"] = (
                    delivery_method
                )

            if payment_method_id:
                payment_method = get_object_or_404(
                    Payment, pk=payment_method_id
                )
                if delivery_method.in_store_pickup:
                    payment_method.price = payment_method.price_promo
                order_serializer.validated_data["payment_method"] = (
                    payment_method
                )

            order_serializer.validated_data["cart_items"] = json.dumps(
                request.data["cart_items"]
            )

            if request.user.is_authenticated:
                order_serializer.validated_data["client"] = request.user

            order_serializer.validated_data["amount"] = (
                delivery_method.price
                + payment_method.price
                + Decimal(cart.get_total_price())
            )
            order_serializer.validated_data["delivery_price"] = (
                delivery_method.price
            )
            order_serializer.validated_data["payment_price"] = (
                payment_method.price
            )
            order = Order.objects.create(
                **order_serializer.validated_data,
            )

            return Response(
                {"order_uid": order.uid}, status=status.HTTP_201_CREATED
            )
        else:
            print(order_serializer.errors)
            return Response(
                {"errors": order_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderDetailsView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(client=user)
        else:
            return Order.objects.none()


class OrderDetailsByUIDView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve an order by UID",
        responses={200: OrderSerializer()},
    )
    def get_queryset(self):
        return Order.objects.all()

    def get_object(self):
        uid = self.kwargs.get("uid")
        queryset = self.get_queryset()
        return get_object_or_404(queryset, uid=uid)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=HTTP_404_NOT_FOUND
            )


class UpdateOrderStatus(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        order_uid = kwargs.get("uid")
        if not order_uid:
            return Response(
                {"detail": "Order ID not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = Order.objects.get(uid=order_uid)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")
        checkout_session_id = request.data.get("checkout_session_id")

        if new_status is None:
            return Response(
                {"detail": "Status not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if checkout_session_id:
            instance.checkout_session_id = checkout_session_id
            instance.save()

        if (
            new_status != instance.status
            and not checkout_session_id
            and instance.email_notification
            and new_status in STATUS_FOR_SEND_EMAIL
        ):
            instance.status = new_status
            instance.save()
            send_email_order_status(instance)
        else:
            if (
                new_status == 3
                and instance.payment_method.payment_online
                and not instance.is_paid
            ):
                instance.status = 4
            else:
                instance.status = new_status
            instance.save()

        return Response(
            {"detail": "Order status updated successfully."},
            status=status.HTTP_200_OK,
        )
