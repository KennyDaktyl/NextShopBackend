from django.urls import path

from .views import (AddOrderItems, CreateOrderView, DeleteOrderItem,
                    OrderDetailsView, OrderListView, UpdateOrderItem)

urlpatterns = [
    # Orders
    path("", OrderListView.as_view(), name="order-list"),
    path("create/", CreateOrderView.as_view(), name="order-create"),
    path("<int:pk>/", OrderDetailsView.as_view(), name="order-details"),
    # Order Items
    path(
        "orders/<int:order_id>/add-item/",
        AddOrderItems.as_view(),
        name="add-order-item",
    ),
    path(
        "order-items/<int:pk>/update/",
        UpdateOrderItem.as_view(),
        name="update-order-item",
    ),
    path(
        "order-items/<int:pk>/delete/",
        DeleteOrderItem.as_view(),
        name="delete-order-item",
    ),
]
