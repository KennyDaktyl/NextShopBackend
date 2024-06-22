# serializers.py
from django.contrib.auth.models import User
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, TokenCreateSerializer
from rest_framework import serializers
from web.models.accounts import Profile
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("username", "email", "password", "re_password")

    def create(self, validated_data):
        print("UserCreateSerializer create method called")
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        print("LoginSerializer validate method called")
        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "User is not active"
                    raise serializers.ValidationError(msg)
            else:
                msg = "Unable to login with given credentials"
                raise serializers.ValidationError(msg)
        else:
            msg = "Must provide username and password"
            raise serializers.ValidationError(msg)
        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        
class UserSerializer(BaseUserCreateSerializer):
    profile = ProfileSerializer()

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ["id", "username", "email", "profile"]
        extra_kwargs = {"password": {"write_only": True}}


class TokenCreateSerializer(TokenCreateSerializer):

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        access = attrs.get("access")
        logger.info("UserCreateSerializer create method called")

        if not refresh or not access:
            msg = "Both refresh and access tokens are required"
            raise serializers.ValidationError(msg)

        return attrs