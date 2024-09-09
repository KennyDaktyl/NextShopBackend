from django.urls import path

from .views import (CreateOrderView, OrderDetailsView, OrderListView,
                    UpdateOrderStatus)

urlpatterns = [
    # Orders
    path("", OrderListView.as_view(), name="order-list"),
    path("create/", CreateOrderView.as_view(), name="order-create"),
    path("<slug:uid>/", OrderDetailsView.as_view(), name="order-details"),
    path(
        "update-status/<slug:uid>/",
        UpdateOrderStatus.as_view(),
        name="update-order-status",
    ),
]
