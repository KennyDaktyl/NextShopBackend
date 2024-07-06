from rest_framework import serializers

from web.categories.serializers import ProductCategorySerializer
from web.images.serializers import ThumbnailSerializer
from web.models.products import Brand, Material, Product, ProductVariant, Size, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name")
        

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ("id", "name")
        
        
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("id", "name")
    


class ProductVariantSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()
    images = ThumbnailSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'name', 'slug', 'color', 'size', 'qty', 'images']

    def get_color(self, obj):
        return obj.get_color_display()
    
     
class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ThumbnailSerializer(many=True)
    variants = ProductVariantSerializer(many=True)
    category = ProductCategorySerializer()
    tags = TagSerializer(many=True)
    brand = BrandSerializer()
    material = MaterialSerializer()
    size = SizeSerializer()
    color = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "images",
            "variants",
            "description",
            "qty",
            "color",
            "tags",
            "brand",
            "material",
            "size",
            "current_price",
            "min_price_last_30",
        )
    
    def get_color(self, obj):
        return obj.get_color_display()
        
    
class ProductListItemSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_price_last_30 = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    # full_image_url = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    image_list_item = ThumbnailSerializer()
    
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "qty",
            "image_list_item",
            "current_price",
            "min_price_last_30",
            "absolute_url",
        )

    # def get_full_image_url(self, obj):
    #     request = self.context.get("request")
    #     if obj.image:
    #         return request.build_absolute_uri(obj.image.url)
    #     return None

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()