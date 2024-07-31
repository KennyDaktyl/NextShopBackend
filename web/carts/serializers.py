from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    item_id = serializers.CharField(required=False)
    name = serializers.CharField()
    slug = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    variant = serializers.CharField(allow_null=True, required=False)
    quantity = serializers.IntegerField()
    image = ThumbnailSerializer()
    url = serializers.CharField()
