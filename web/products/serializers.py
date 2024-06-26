from rest_framework import serializers

from web.models.categories import Category
from web.models.products import Product


class CategorySerializer(serializers.ModelSerializer):
    is_parent = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    back_link = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "has_parent",
            "is_parent",
            "get_products_count",
            "has_children",
            "full_path",
            "back_link",
        )

    def get_is_parent(self, obj):
        return obj.children.exists()
    
    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_back_link(self, obj):
        return obj.get_back_link()


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "description",
        )
        

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
        )
        
        
class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_price_last_30 = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    full_image_url = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

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
             "absolute_url",
        )

    def get_full_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()