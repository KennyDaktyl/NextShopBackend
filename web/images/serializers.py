from rest_framework import serializers

from web.models.images import Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = [
            "id",
            "width",
            "height",
            "url",
            "alt",
            "title",
            "height_expected",
            "width_expected",
        ]

    def get_url(self, obj):
        request = self.context.get("request")

        if request is None:
            return None

        if isinstance(obj, dict):
            return request.build_absolute_uri(obj["url"])

        if obj.oryg_image:
            return request.build_absolute_uri(obj.oryg_image.url)

        return None


class ThumbnailURLSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = [
            "url",
        ]

    def get_url(self, obj):
        request = self.context.get("request")

        if request is None:
            return None

        if isinstance(obj, dict):
            return request.build_absolute_uri(obj["url"])

        if obj.oryg_image:
            return request.build_absolute_uri(obj.oryg_image.url)

        return None
