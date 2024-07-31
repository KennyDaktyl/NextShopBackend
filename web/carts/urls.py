from django.urls import path

from .views import (
    cart_items,
    create_cart,
    remove_cart,
    total_price,
    update_cart,
    update_item_qty,
)

urlpatterns = [
    path("create", create_cart, name="create_cart"),
    path("update", update_cart, name="update_cart"),
    path("update-item-qty", update_item_qty, name="update_item_qty"),
    path("total-price", total_price, name="total_price"),
    path("cart-items", cart_items, name="cart_items"),
    path("remove-cart", remove_cart, name="remove_cart"),
]
