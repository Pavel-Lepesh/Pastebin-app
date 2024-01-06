from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
