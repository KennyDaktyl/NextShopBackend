from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.categories import Category


class CategorySerializer(serializers.ModelSerializer):
    is_parent = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    back_link = serializers.SerializerMethodField()
    image_list_item = ThumbnailSerializer()

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
            "image_list_item",
        )

    def get_is_parent(self, obj):
        return obj.children.exists()

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_back_link(self, obj):
        return obj.get_back_link()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "description",
        )


class ProductCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "full_path")

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

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
