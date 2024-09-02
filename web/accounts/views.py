from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (LoginSerializer, UserAddressDataSerializer,
                          UserAddressSerializer, UserFullDataSerializer,
                          UserInvoiceDataSerializer, UserMainDataSerializer,
                          UserPasswordSerializer, UserRegisterSerializer)


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


class UserRegistrationView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Registration successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
