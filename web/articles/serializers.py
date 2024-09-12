from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.articles import Article
from web.products.serializers import ProductCategorySerializer


class ArticlesListSerializer(serializers.ModelSerializer):
    image_listing = ThumbnailSerializer()
    category = ProductCategorySerializer()

    class Meta:
        model = Article
        fields = (
            "id",
            "name",
            "description",
            "slug",
            "created_date",
            "category",
            "image_listing",
            "full_path",
        )


class ArticlesDetailsSerializer(serializers.ModelSerializer):
    gallery = ThumbnailSerializer(many=True)
    image = ThumbnailSerializer()
    category = ProductCategorySerializer()

    class Meta:
        model = Article
        fields = (
            "id",
            "name",
            "description",
            "slug",
            "created_date",
            "category",
            "content",
            "meta_description",
            "meta_title",
            "image",
            "gallery",
            "full_path",
        )
