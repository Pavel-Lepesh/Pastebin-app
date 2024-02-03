from rest_framework import serializers


class GetCommentSerializer(serializers.Serializer):
    note_comment_id = serializers.IntegerField()
    user = serializers.CharField(max_length=255)
    body = serializers.CharField()
    likes = serializers.IntegerField(default=0)
    dislikes = serializers.IntegerField(default=0)
    created = serializers.DateTimeField()


class PostOrUpdateCommentSerializer(serializers.Serializer):
    body = serializers.CharField()


class RateCommentSerializer(serializers.Serializer):
    likes = serializers.IntegerField(default=0)
    dislikes = serializers.IntegerField(default=0)


class NotFound404Serializer(serializers.Serializer):
    detail = serializers.CharField(default='Not found.')


class NotAuthorized401Serializer(serializers.Serializer):
    detail = serializers.CharField(default='Authentication credentials were not provided.')


class Forbidden403Serializer(serializers.Serializer):
    detail = serializers.CharField(default='You do not have permission to perform this action.')


class BadRequest400Serializer(serializers.Serializer):
    error_field = serializers.ListField()


class CommonBadRequest400Serializer(serializers.Serializer):
    detail = serializers.CharField()
