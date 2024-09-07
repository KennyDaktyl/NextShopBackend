import uuid

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.carts.cart import Cart
from web.models.products import Product
from web.models.products import ProductVariant as Variant

from .serializers import (CartCreateSerializer, CartItemSerializer,
                          CartUpdateSerializer, RemoveItemSerializer,
                          UpdateCartItemQtySerializer)


class CartCreateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CartCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data.get("product_id")
            quantity = serializer.validated_data.get("quantity")
            variant_id = serializer.validated_data.get("variant_id")
            selected_option = serializer.validated_data.get(
                "selected_option", None
            )
            info = serializer.validated_data.get("info")
            product = get_object_or_404(Product, id=product_id)
            variant = None
            if variant_id:
                variant = get_object_or_404(Variant, id=variant_id)
                available_quantity = variant.qty
            else:
                available_quantity = product.qty

            if quantity > available_quantity:
                return Response(
                    {"error": "Requested quantity exceeds available stock"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            image = (
                product.item_image if variant is None else variant.item_image
            )

            if selected_option:
                selected_label = selected_option.get("option_name")
                selected_option_value = selected_option.get("value_name")
                selected_option = (
                    selected_label + " - " + selected_option_value
                )

            if variant:
                variant = product.variant_label + " - " + variant.name

            cart_item_data = {
                "id": product_id,
                "name": product.name,
                "slug": product.slug,
                "price": str(product.current_price),
                "variant": variant,
                "selected_option": selected_option,
                "quantity": quantity,
                "available_quantity": available_quantity,
                "image": image,
                "url": product.full_path,
                "free_delivery": product.free_delivery,
                "info": info,
            }

            cart_item_serializer = CartItemSerializer(
                cart_item_data, context={"request": request}
            )
            cart_item = cart_item_serializer.data

            cart = Cart(request)
            cart.add_product(cart_item)

            unique_cart_id = str(uuid.uuid4())
            response = JsonResponse({"cart_id": unique_cart_id, "free_delivery": product.free_delivery}, status=201)
            response.set_cookie(
                "sessionid",
                request.session.session_key,
                httponly=True,
                samesite="Lax",
            )
            return response
        return JsonResponse(serializer.errors, status=400)


class CartUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CartUpdateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            cart_id = serializer.validated_data.get("cart_id")
            product_id = serializer.validated_data.get("product_id")
            quantity = serializer.validated_data.get("quantity")
            variant_id = serializer.validated_data.get("variant_id")
            selected_option = serializer.validated_data.get(
                "selected_option", None
            )
            info = serializer.validated_data.get("info")
            cart = Cart(request)

            if not cart:
                return JsonResponse(
                    {"error": "Cart ID not provided"}, status=400
                )

            product = get_object_or_404(Product, id=product_id)
            variant = None
            if variant_id:
                variant = get_object_or_404(Variant, id=variant_id)
                available_quantity = variant.qty
            else:
                available_quantity = product.qty
            existing_quantity = cart.get_product_quantity(product_id, variant)

            if quantity + existing_quantity > available_quantity:
                return Response(
                    {
                        "error": "Brak wystarczającej ilości towaru na magazynie"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            image = (
                product.item_image if variant is None else variant.item_image
            )

            if selected_option:
                selected_label = selected_option.get("option_name")
                selected_option_value = selected_option.get("value_name")
                selected_option = (
                    selected_label + " - " + selected_option_value
                )

            if variant:
                variant = product.variant_label + " - " + variant.name

            cart_item_data = {
                "id": product_id,
                "name": product.name,
                "slug": product.slug,
                "price": str(product.current_price),
                "variant": variant,
                "selected_option": selected_option,
                "quantity": quantity,
                "available_quantity": available_quantity,
                "image": image,
                "url": product.full_path,
                "free_delivery": product.free_delivery,
                "info": info,
            }

            cart_item_serializer = CartItemSerializer(
                cart_item_data, context={"request": request}
            )
            cart_item = cart_item_serializer.data

            cart.add_product(cart_item)
            return JsonResponse(
                {"cart_id": cart_id, "free_delivery": product.free_delivery},
                status=200,
            )
        return JsonResponse(serializer.errors, status=400)


class GetCartItemsView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart_items = cart.get_items()
        free_delivery = cart.is_free_delivery()
        cart_items_serializer = CartItemSerializer(
            cart_items, many=True, context={"request": request}
        )
        return JsonResponse(
            {
                "cart_items": cart_items_serializer.data,
                "free_delivery": free_delivery,
            },
            status=200,
        )


class TotalPriceView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        total_price = cart.get_total_price()
        return JsonResponse({"total_price": total_price}, status=200)


class CartDeleteView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.delete_session()
        return JsonResponse({"message": "Cart deleted"}, status=200)


class UpdateCartItemQtyView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UpdateCartItemQtySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item_id = serializer.validated_data.get("item_id")
            quantity = serializer.validated_data.get("quantity")

            cart = Cart(request)
            cart.update_item_qty(item_id, quantity)
            return JsonResponse({"message": "Item qty updated"}, status=200)
        return JsonResponse(serializer.errors, status=400)


class RemoveItemView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RemoveItemSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item_id = serializer.validated_data.get("item_id")

            cart = Cart(request)
            cart.remove_item(item_id)
            return JsonResponse({"message": "Item removed"}, status=200)
        return JsonResponse(serializer.errors, status=400)


create_cart = CartCreateView.as_view()
update_cart = CartUpdateView.as_view()
cart_items = GetCartItemsView.as_view()
update_item_qty = UpdateCartItemQtyView.as_view()
total_price = TotalPriceView.as_view()
remove_cart = CartDeleteView.as_view()
remove_item = RemoveItemView.as_view()
