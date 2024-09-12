from django.urls import path

from .views import (UserFullDataView, UserLoginView,
                    UserProfileUpdateInvoiceDataView, UserProfileUpdateView,
                    UserProfileView, UserUpdateMainDataView,
                    UserUpdatePassowrdView)

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    # path("register/", UserRegistrationView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("full-data/", UserFullDataView.as_view(), name="full-data"),
    path(
        "update-main-data/",
        UserUpdateMainDataView.as_view(),
        name="update-main-data",
    ),
    path(
        "update-password/",
        UserUpdatePassowrdView.as_view(),
        name="update-password",
    ),
    path(
        "update-address/",
        UserProfileUpdateView.as_view(),
        name="update-address",
    ),
    path(
        "update-invoice-data/",
        UserProfileUpdateInvoiceDataView.as_view(),
        name="update-invoice-data",
    ),
]
