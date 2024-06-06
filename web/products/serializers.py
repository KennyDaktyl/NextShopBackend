from rest_framework import serializers

from web.models.products import Product


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_price_last_30 = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "qty",
            "current_price",
            "min_price_last_30",
        )

    def get_category(self, obj):
        return obj.category.name
