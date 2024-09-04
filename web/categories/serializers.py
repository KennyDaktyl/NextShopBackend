from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.categories import Category
from web.products.serializers import ProductOnFirstPageSerializer


class CategorySerializer(serializers.ModelSerializer):
    is_parent = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    back_link = serializers.SerializerMethodField()
    image = ThumbnailSerializer()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "item_label",
            "slug",
            "description",
            "seo_text",
            "has_parent",
            "is_parent",
            "products_count",
            "has_children",
            "full_path",
            "back_link",
            "image",
        )

    def get_is_parent(self, obj):
        return obj.children.exists()

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_back_link(self, obj):
        return obj.get_back_link()


class CategoryPathSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("full_path",)

    def get_full_path(self, obj):
        return obj.get_full_path()


class SubcategoryOnFirstPageSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "products_count",
            "full_path",
        )

    def get_full_path(self, obj):
        return obj.get_full_path()


class CategoryListOnFirstPageSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()
    image = ThumbnailSerializer()
    all_subcategories = SubcategoryOnFirstPageSerializer(many=True)
    products_on_first_page = ProductOnFirstPageSerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "seo_text",
            "all_subcategories",
            "full_path",
            "image",
            "products_on_first_page",
        )

    def get_full_path(self, obj):
        return obj.get_full_path()


class CategoriesOnFirstPageSerializer(serializers.Serializer):
    categories = CategoryListOnFirstPageSerializer(many=True)


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "name",
            "description",
            "seo_text",
            "seo_text",
            "has_children",
            "full_path",
        )

    def get_full_path(self, obj):
        return obj.get_full_path()


class ProductsByCategorySerializer(serializers.ModelSerializer):
    is_parent = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    back_link = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "item_label",
            "slug",
            "description",
            "seo_text",
            "has_parent",
            "is_parent",
            "products_count",
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
