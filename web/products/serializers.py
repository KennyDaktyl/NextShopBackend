from django.conf import settings
from rest_framework import serializers

from django.db.models import Avg
from web.images.serializers import ThumbnailSerializer, ThumbnailURLSerializer
from web.models.products import (
    Brand,
    Category,
    Material,
    Product,
    ProductOptionItem,
    ProductReview,
    ProductVariant,
    Size,
    Tag,
)


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
        fields = ("full_path", "modified_date")


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Możemy wyświetlać nazwę użytkownika lub e-mail

    class Meta:
        model = ProductReview
        fields = ['user', 'rating', 'comment', 'created_at']
        

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
    free_delivery_threshold = serializers.FloatField()
    free_delivery_threshold_passed = serializers.BooleanField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = (
            "id",
            "meta_title",
            "meta_description",
            "h1_tag",
            "name",
            "slug",
            "category",
            "images",
            "variants",
            "description",
            "seo_text",
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
            "full_path",
            "is_service",
            "free_delivery_threshold",
            "free_delivery_threshold_passed",
            "average_rating",
            "review_count",
            "reviews",
        )

    def get_color(self, obj):
        return obj.get_color_display()
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()


class ProductListItemSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_price_last_30 = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    # full_image_url = serializers.SerializerMethodField()
    image = ThumbnailSerializer()
    variants = ProductListVariantSerializer(many=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "seo_text",
            "image",
            "current_price",
            "min_price_last_30",
            "full_path",
            "variants",
            "show_variant_label",
            "variant_label",
            "full_path",
            "is_service",
            "average_rating",
            "review_count",
            "reviews",
        )

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()
    
    
class ProductOnFirstPageSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    image = ThumbnailSerializer()
    variants = ProductListVariantSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "image",
            "current_price",
            "min_price_last_30",
            "full_path",
            "variants",
            "show_variant_label",
            "full_path",
        )


class ProductGoogleMerchantSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', default='')
    category = serializers.CharField(source='category.name', default='')
    image = ThumbnailURLSerializer()
    availability = serializers.SerializerMethodField()
    condition = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField() 
    google_product_category = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField() 
    
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'link',
            'image',
            'price',
            'availability',
            'condition',
            'brand',
            'category',
            'google_product_category'
        )
    
    def get_description(self, obj):
        if obj.description:
            return obj.description
        else:
            return "Produkt z kategorii " + obj.category.name
        
    def get_availability(self, obj):
        return 'in stock' if obj.qty > 0 else 'out of stock'

    def get_condition(self, obj):
        return 'new'

    def get_price(self, obj):
        return f"{obj.current_price} PLN"
    
    def get_link(self, obj):
        return f"{settings.DOMAIN}{obj.full_path}"
    
    def get_image(self, obj):
        return obj.image.url
    
    def get_google_product_category(self, obj):
        if not obj.google_product_category:
            if 'klucz' in obj.name.lower():
                return '852'  
            elif 'pieczątka' in obj.name.lower():
                return '6003' 
            else:
                return '852'  
        else:
            return obj.google_product_category
        