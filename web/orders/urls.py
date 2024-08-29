from django.urls import path

from .views import (CreateOrderView, OrderDetailsView, OrderListView,
                    UpdateOrderStatus)

urlpatterns = [
    # Orders
    path("", OrderListView.as_view(), name="order-list"),
    path("create/", CreateOrderView.as_view(), name="order-create"),
    path("<int:pk>/", OrderDetailsView.as_view(), name="order-details"),
    path(
        "update-status/<int:pk>/",
        UpdateOrderStatus.as_view(),
        name="update-order-status",
    ),
]
