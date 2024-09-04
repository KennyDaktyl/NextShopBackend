from rest_framework import serializers

from web.images.serializers import ThumbnailSerializer
from web.models.products import ProductOption, ProductOptionItem


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    item_id = serializers.UUIDField(format="hex_verbose", required=False)
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField()
    price = serializers.CharField(max_length=20)
    variant = serializers.CharField(
        max_length=255, required=False, allow_null=True
    )
    selected_option = serializers.CharField(
        max_length=255, required=False, allow_null=True
    )
    quantity = serializers.IntegerField()
    available_quantity = serializers.IntegerField()
    image = ThumbnailSerializer()
    url = serializers.CharField(max_length=255)
    free_delivery = serializers.BooleanField(default=False)


class UpdateCartItemQtySerializer(serializers.Serializer):
    item_id = serializers.UUIDField(format="hex_verbose")
    quantity = serializers.IntegerField()


class CartCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    selected_option = serializers.DictField(
        child=serializers.IntegerField(), required=False
    )
    free_delivery = serializers.BooleanField(default=False)

    def validate_selected_option(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Invalid format for selected_option. Expected a dictionary."
            )
        if "option_id" not in value or "value_id" not in value:
            raise serializers.ValidationError(
                "selected_option must contain 'option_id' and 'value_id'."
            )
        if not isinstance(value["option_id"], int) or not isinstance(
            value["value_id"], int
        ):
            raise serializers.ValidationError(
                "'option_id' and 'value_id' must be integers."
            )
        return value

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        selected_option = ret.get("selected_option", {})
        if selected_option:
            option = ProductOption.objects.get(id=selected_option["option_id"])
            value = ProductOptionItem.objects.get(
                id=selected_option["value_id"]
            )
            ret["selected_option"] = {
                "option_name": option.name,
                "value_name": value.name,
            }
        return ret


class CartUpdateSerializer(CartCreateSerializer):
    cart_id = serializers.CharField()


class RemoveItemSerializer(serializers.Serializer):
    item_id = serializers.UUIDField(format="hex_verbose", required=False)
