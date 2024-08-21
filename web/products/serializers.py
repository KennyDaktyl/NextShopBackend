from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.products import (Brand, Category, Material, Product,
                                 ProductOptionItem, ProductVariant, Size, Tag)


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
    tags = TagSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "name",
            "slug",
            "color",
            "size",
            "qty",
            "images",
            "tags",
            "is_main",
        ]

    def get_color(self, obj):
        return obj.get_color_display()


class ProductListVariantSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ["name", "slug", "color", "size"]

    def get_color(self, obj):
        return obj.get_color_display()


class ProductOptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptionItem
        fields = ["id", "name"]


class ProductOptionItemsSerializer(serializers.ModelSerializer):
    options = ProductOptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOptionItem
        fields = ["id", "name", "options"]


class SelectedOptionSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()
    value_id = serializers.IntegerField()


class ProductCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "full_path")

    def get_full_path(self, obj):
        return obj.get_full_path()


class ProductsPathListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ("get_absolute_url",)
        
    
class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ThumbnailSerializer(many=True)
    variants = ProductVariantSerializer(many=True)
    category = ProductCategorySerializer()
    tags = TagSerializer(many=True)
    brand = BrandSerializer()
    material = MaterialSerializer()
    size = SizeSerializer()
    color = serializers.SerializerMethodField()
    product_option = ProductOptionItemsSerializer()

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
            "show_variant_label",
            "variant_label",
            "product_option",
            "free_delivery",
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
    image = ThumbnailSerializer()
    variants = ProductListVariantSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "image",
            "current_price",
            "min_price_last_30",
            "absolute_url",
            "variants",
            "show_variant_label",
            "variant_label",
        )

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
