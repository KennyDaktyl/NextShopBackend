from rest_framework import serializers

from web.models.images import Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = ["id", "width", "height", "url", "alt", "title"]

    def get_url(self, obj):
        request = self.context.get("request")
        if isinstance(obj, dict):
            return request.build_absolute_uri(obj["url"])
        if obj.oryg_image:
            return request.build_absolute_uri(obj.oryg_image.url)
        return None
