from rest_framework import serializers

from web.models.products import Product


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug"
        )
    
    
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_price_last_30 = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    full_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "qty",
            "full_image_url",
            "current_price",
            "min_price_last_30",
        )


    def get_full_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None