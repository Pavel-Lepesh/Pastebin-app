from rest_framework import serializers


class BadRequest400Serializer(serializers.Serializer):
    error_field = serializers.ListField()
