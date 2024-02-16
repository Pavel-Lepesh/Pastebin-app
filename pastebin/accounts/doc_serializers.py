from rest_framework import serializers


class BadRequest400Serializer(serializers.Serializer):
    error_field = serializers.ListField()


class NotAuthorized401Serializer(serializers.Serializer):
    detail = serializers.CharField(default='Authentication credentials were not provided.')
