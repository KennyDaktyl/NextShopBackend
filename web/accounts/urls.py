from django.urls import path

from .views import UserLoginView, UserProfileView, UserRegistrationView

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]
