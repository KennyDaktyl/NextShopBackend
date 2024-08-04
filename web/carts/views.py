# views.py
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

from .serializers import CartItemSerializer


class CartCreateView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        body = request.data
        product_id = body.get("product_id")
        quantity = int(body.get("quantity", 1))
        variant_id = body.get("variant_id")

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

        image = product.item_image if variant is None else variant.item_image

        cart_item_data = {
            "id": product_id,
            "name": product.name,
            "slug": product.slug,
            "price": str(product.current_price),
            "variant": variant.name if variant else None,
            "quantity": quantity,
            "available_quantity": available_quantity,
            "image": image,
            "url": product.get_absolute_url(),
        }

        cart_item_serializer = CartItemSerializer(
            cart_item_data, context={"request": request}
        )
        cart_item = cart_item_serializer.data

        cart = Cart(request)
        cart.add_product(cart_item)

        unique_cart_id = str(uuid.uuid4())
        response = JsonResponse({"cart_id": unique_cart_id}, status=201)

        response.set_cookie(
            "sessionid",
            request.session.session_key,
            httponly=True,
            samesite="Lax",
        )
        return response


class CartUpdateView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        body = request.data

        cart_id = body.get("cart_id")
        product_id = body.get("product_id")
        quantity = int(body.get("quantity", 1))
        variant_id = body.get("variant_id")

        cart = Cart(request)

        if not cart:
            return JsonResponse({"error": "Cart ID not provided"}, status=400)

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
                {"error": "Brak wystarczającej ilości towaru na magazynie"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = product.item_image if variant is None else variant.item_image

        cart_item_data = {
            "id": product_id,
            "name": product.name,
            "slug": product.slug,
            "price": str(product.current_price),
            "variant": variant.name if variant else None,
            "quantity": quantity,
            "available_quantity": available_quantity,
            "image": image,
            "url": product.get_absolute_url(),
        }

        cart_item_serializer = CartItemSerializer(
            cart_item_data, context={"request": request}
        )
        cart_item = cart_item_serializer.data

        cart.add_product(cart_item)
        return JsonResponse({"cart_id": cart_id}, status=200)


class GetCartItemsView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart_items = cart.get_items()
        cart_items_serializer = CartItemSerializer(
            cart_items, many=True, context={"request": request}
        )
        return JsonResponse(
            {"cart_items": cart_items_serializer.data}, status=200
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

    def post(self, request, *args, **kwargs):
        body = request.data

        cart = Cart(request)
        item_id = body.get("item_id")
        qty = body.get("quantity")

        cart.update_item_qty(item_id, qty)
        return JsonResponse({"message": "Item qty updated"}, status=200)


class RemoveItemView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        body = request.data

        cart = Cart(request)
        item_id = body.get("item_id")

        cart.remove_item(item_id)
        return JsonResponse({"message": "Item removed"}, status=200)


create_cart = CartCreateView.as_view()
update_cart = CartUpdateView.as_view()
cart_items = GetCartItemsView.as_view()
update_item_qty = UpdateCartItemQtyView.as_view()
total_price = TotalPriceView.as_view()
remove_cart = CartDeleteView.as_view()
remove_item = RemoveItemView.as_view()
