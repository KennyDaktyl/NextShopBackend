from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from web.deliveries.serializers import DeliveriesForOrderSerializer, DeliveriesSerializer
from web.images.serializers import ThumbnailSerializer
from web.models.orders import Order, OrderItem
from web.payments.serializers import PaymentMethodsForOrdersSerializer, PaymentMethodsSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrdersUserSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    delivery_method = DeliveriesForOrderSerializer()
    payment_method = PaymentMethodsForOrdersSerializer()

    class Meta:
        model = Order
        fields = "__all__"
        
        
class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    delivery_method = DeliveriesSerializer()
    payment_method = PaymentMethodsSerializer()

    class Meta:
        model = Order
        fields = "__all__"


class CreateOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        exclude = ["created_date", "updated_date", "client", "status"]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        return order


class DecimalField(serializers.Field):
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        try:
            return Decimal(data)
        except InvalidOperation:
            self.fail("invalid")


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)
    price = DecimalField()
    variant = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    selected_option = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    quantity = serializers.IntegerField()
    image = ThumbnailSerializer(allow_null=True, required=False)
    url = serializers.CharField()


class CreateOrderSerializer(serializers.Serializer):
    client_name = serializers.CharField(max_length=255)
    client_email = serializers.EmailField()
    client_mobile = serializers.CharField(max_length=15)
    delivery_price = DecimalField()
    payment_price = DecimalField()
    cart_items_price = DecimalField()
    amount = DecimalField()
    delivery_method = serializers.CharField(max_length=10)
    payment_method = serializers.CharField(max_length=10)
    cart_items = CartItemSerializer(many=True)
    info = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )

    inpost_box_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )

    street = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    house_number = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    local_number = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    city = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    postal_code = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )

    invoice = serializers.BooleanField()
    company = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    company_payer = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    nip = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    invoice_street = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    invoice_house_number = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    invoice_local_number = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    invoice_city = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    invoice_postal_code = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )


class OrderUpdateStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
