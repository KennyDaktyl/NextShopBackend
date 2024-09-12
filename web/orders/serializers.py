from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

from django.conf import settings
from rest_framework import serializers

from web.deliveries.serializers import (DeliveriesForOrderSerializer,
                                        DeliveriesSerializer)
from web.images.serializers import ThumbnailSerializer
from web.models.orders import Invoice, Order, OrderItem
from web.payments.serializers import (PaymentMethodsForOrdersSerializer,
                                      PaymentMethodsSerializer)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class InvoiceSerializer(serializers.Serializer):
    pdf = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = "pdf"

    def get_pdf(self, obj):
        request = self.context.get("request", None)

        if obj.pdf:
            if request:
                full_path = urljoin(
                    request.build_absolute_uri("/"), obj.pdf.url
                )
            else:
                site_url = getattr(
                    settings, "SITE_URL", "http://127.0.0.1:8000/"
                )
                full_path = urljoin(site_url, obj.pdf.url)
            return full_path
        return None


class OrdersUserSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    delivery_method = DeliveriesForOrderSerializer()
    payment_method = PaymentMethodsForOrdersSerializer()
    invoice = InvoiceSerializer()

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "created_date",
            "delivery_method",
            "payment_method",
            "amount",
            "invoice",
            "info",
            "order_number",
            "delivery_price",
            "payment_price",
            "cart_items_price",
            "cart_items",
            "is_paid",
            "inpost_box_id",
            "street",
            "house_number",
            "local_number",
            "city",
            "postal_code",
            "make_invoice",
            "company",
            "company_payer",
            "nip",
            "invoice_street",
            "invoice_house_number",
            "invoice_local_number",
            "invoice_city",
            "invoice_postal_code",
        )


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
    info = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )


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

    make_invoice = serializers.BooleanField()
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
