from rest_framework import serializers
from django.db.models import Avg

from web.images.serializers import ThumbnailSerializer
from web.models.categories import Category
from web.products.serializers import ProductOnFirstPageSerializer, ProductReviewSerializer



class CategoryListingSerializer(serializers.ModelSerializer):
    is_parent = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    image = ThumbnailSerializer()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "item_label",
            "full_path",
            "image",
            "is_parent",
            "products_count",
            "has_children",
        )

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_is_parent(self, obj):
        return obj.children.exists()
    
    
class CategorySerializer(CategoryListingSerializer):
   
    back_link = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "meta_title",
            "meta_description",
            "h1_tag",
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

    def get_back_link(self, obj):
        return obj.get_back_link()


class CategoryPathSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("full_path", "modified_date")

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
            "order",
            "description",
            "products_count",
            "full_path",
        )

    def get_full_path(self, obj):
        return obj.get_full_path()


class CategoryListOnFirstPageSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()
    image = ThumbnailSerializer()
    all_subcategories = serializers.SerializerMethodField()
    products_on_first_page = ProductOnFirstPageSerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "all_subcategories",
            "full_path",
            "image",
            "products_on_first_page",
        )

    def get_all_subcategories(self, obj):
        def get_subcategories_recursive(category):
            children = category.children.filter(is_active=True).order_by("order")
            result = []
            for child in children:
                result.append(SubcategoryOnFirstPageSerializer(
                    child, context=self.context
                ).data)
                result.extend(get_subcategories_recursive(child))
            return result
        all_subcategories = get_subcategories_recursive(obj)

        all_subcategories_sorted = sorted(all_subcategories, key=lambda x: x["name"])
        return all_subcategories_sorted

    def get_full_path(self, obj):
        return obj.get_full_path()


class CategoriesOnFirstPageSerializer(serializers.Serializer):
    categories = CategoryListOnFirstPageSerializer(many=True)


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()
    image = ThumbnailSerializer()

    class Meta:
        model = Category
        fields = (
            "name",
            "meta_title",
            "meta_description",
            "description",
            "image",
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
