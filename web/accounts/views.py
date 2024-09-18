from django.contrib.auth import authenticate, login
from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from web.functions import send_activation_info_for_owner
from web.models.accounts import Profile

from .serializers import (
    LoginSerializer,
    UserAddressDataSerializer,
    UserAddressSerializer,
    UserFullDataSerializer,
    UserInvoiceDataSerializer,
    UserMainDataSerializer,
    UserPasswordSerializer,
)


class UserLoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response(
                {"message": "Login successful"}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserRegistrationViewSet(UserViewSet):

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )
        Profile.objects.get_or_create(user=user, send_emails=True)

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)

        email_title = "Nowy użytkownik zarejestrował się w systemie"
        email_message = (
            f"Użytkownik: {user.username} został zarejestrowany w systemie"
        )
        send_activation_info_for_owner(email_title, email_message, user)

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        email_title = "Nowy użytkownik aktywował konto"
        email_message = f"Użytkownik: {user.username} aktywował konto"
        send_activation_info_for_owner(email_title, email_message, user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(GenericAPIView):
    serializer_class = UserAddressDataSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserAddressDataSerializer(user)
        return Response(serializer.data)


class UserFullDataView(GenericAPIView):
    serializer_class = UserFullDataSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserFullDataSerializer(user)
        return Response(serializer.data)


class UserUpdateMainDataView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserMainDataSerializer

    def post(self, request):
        serializer = UserMainDataSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.email = serializer.validated_data.get("email")
            user.first_name = serializer.validated_data.get("first_name")
            user.last_name = serializer.validated_data.get("last_name")
            user.save()

            profile = Profile.objects.get(user=user)
            profile.mobile = serializer.validated_data.get("mobile")
            profile.save()

            return Response(
                {"message": "Update data successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdatePassowrdView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserPasswordSerializer

    def post(self, request):
        serializer = UserPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data.get("new_password")

            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Update data successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserAddressSerializer

    def post(self, request):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            profile = request.user.profile
            profile.__dict__.update(serializer.validated_data)
            profile.save()
            return Response(
                {"message": "Update data successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateInvoiceDataView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserInvoiceDataSerializer

    def post(self, request):
        serializer = UserInvoiceDataSerializer(data=request.data)
        if serializer.is_valid():
            profile = request.user.profile
            profile.__dict__.update(serializer.validated_data)
            profile.make_invoice = True
            profile.save()
            return Response(
                {"message": "Update data successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
