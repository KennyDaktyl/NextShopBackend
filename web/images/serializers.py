from rest_framework import serializers

from web.models.images import Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = ["id", "width", "height", "image_url", "alt", "title"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if isinstance(obj, dict):
            return request.build_absolute_uri(obj["image_url"])
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
