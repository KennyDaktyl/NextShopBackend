from rest_framework import serializers
from web.models.products import Product


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "name", "slug", "category", "description", "qty", "current_price", "min_price_last_30")

    def get_category(self, obj):
        return obj.category.name
