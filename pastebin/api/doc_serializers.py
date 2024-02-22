from rest_framework import serializers


class UpdateNoteSerializer(serializers.Serializer):
    updated_field = serializers.CharField()


class BaseNoteSerializer(serializers.Serializer):
    content = serializers.CharField()


class CreateNoteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    availability = serializers.ChoiceField(choices=['public', 'private'], default='public')
    expiration = serializers.IntegerField(default=None, required=False)


class NoteLikesSerializer(serializers.Serializer):
    likes = serializers.IntegerField(default=0)


class NoteMetaDataSerializer(serializers.Serializer):
    views = serializers.IntegerField(default=0)
    stars = serializers.IntegerField(default=0)
    likes = serializers.IntegerField(default=0)


class ListCommentsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    note = serializers.IntegerField()
    user = serializers.IntegerField()
    body = serializers.CharField()
    children = serializers.ListField(child=serializers.DictField(default={'key': 'value'}))


class MyStarsSerializer(serializers.Serializer):
    my_stars = serializers.DictField()


class AddStarSerializer(serializers.Serializer):
    save_to_stars = serializers.CharField()


class PostCommentSerializer(serializers.Serializer):
    body = serializers.CharField()
    parent = serializers.IntegerField(required=False)


class UpdateCommentSerializer(serializers.Serializer):
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
