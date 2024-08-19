from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.heros import Hero


class HeroSerializer(serializers.ModelSerializer):
    image = ThumbnailSerializer()

    class Meta:
        model = Hero
        fields = ("id", "title", "description", "image", "link", "is_active")


class ContactEmailSerializer(serializers.Serializer):
    title = serializers.CharField()
    email = serializers.EmailField()
    message = serializers.CharField()
