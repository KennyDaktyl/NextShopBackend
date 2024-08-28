from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.payments import Payment


class PaymentMethodsSerializer(serializers.ModelSerializer):
    image = ThumbnailSerializer()

    class Meta:
        model = Payment
        fields = ("id", "name", "image", "price", "payment_on_delivery", "payment_online")
