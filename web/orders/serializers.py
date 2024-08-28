from rest_framework import serializers
from decimal import Decimal, InvalidOperation

from web.images.serializers import ThumbnailSerializer
from web.models.orders import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

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
        return str(value)  # Można zmienić na float(value) dla większej precyzji

    def to_internal_value(self, data):
        try:
            return Decimal(data)
        except InvalidOperation:
            self.fail('invalid')

class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)
    price = DecimalField()  
    variant = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    selected_option = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
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
    inpost_box_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    info = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
