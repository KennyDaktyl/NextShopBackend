import re

from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.heros import Hero
from web.models.inquiries import KeyPhotoInquiry

PHONE_REGEX = re.compile(r"^(\+48[\s-]?)?(\d[\s-]?){9}$")
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_phone_number(value):
    if not PHONE_REGEX.match(value.strip()):
        raise serializers.ValidationError("Podaj poprawny numer telefonu.")
    return value


def validate_photo_size(value):
    if value.size > MAX_PHOTO_SIZE:
        raise serializers.ValidationError("Zdjęcie jest za duże (limit 10 MB).")
    return value


class HeroSerializer(serializers.ModelSerializer):
    image = ThumbnailSerializer()

    class Meta:
        model = Hero
        fields = (
            "id",
            "title",
            "description",
            "image",
            "link",
            "link_text",
            "is_active",
        )


class StampDesignLineSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=60)
    font = serializers.CharField()
    size = serializers.IntegerField()
    bold = serializers.BooleanField()
    italic = serializers.BooleanField()


class ContactEmailSerializer(serializers.Serializer):
    title = serializers.CharField()
    email = serializers.EmailField()
    message = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    stamp_design = StampDesignLineSerializer(many=True, required=False, min_length=1, max_length=8)


class KeyPhotoInquirySerializer(serializers.ModelSerializer):
    phone = serializers.CharField(validators=[validate_phone_number])
    photo = serializers.ImageField(validators=[validate_photo_size])

    class Meta:
        model = KeyPhotoInquiry
        fields = ("photo", "email", "phone", "note")
