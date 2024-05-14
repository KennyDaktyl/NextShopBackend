from rest_framework import serializers
from web.models.products import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "description", "current_price", "min_price_last_30")