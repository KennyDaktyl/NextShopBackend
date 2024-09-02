from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.deliveries import Delivery


class DeliveriesSerializer(serializers.ModelSerializer):
    image = ThumbnailSerializer()

    class Meta:
        model = Delivery
        fields = (
            "id",
            "name",
            "image",
            "price",
            "price_promo",
            "inpost_box",
            "in_store_pickup",
        )


class DeliveriesForOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = (
            "name",
            "price",
            "price_promo",
            "inpost_box",
            "in_store_pickup",
        )
