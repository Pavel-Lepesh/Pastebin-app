from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Note, Comment
from .s3_storage import s3_storage
from django.contrib.auth.models import User
from django.core.cache import caches
from django.utils import timezone
from datetime import timedelta


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ('note_comment_id', 'note', 'user', 'body')


class GetCommentSerializer(Serializer):
    note_comment_id = serializers.IntegerField()
    user = serializers.CharField(max_length=255)
    body = serializers.CharField()
    likes = serializers.IntegerField(default=0)
    dislikes = serializers.IntegerField(default=0)
    created = serializers.DateTimeField()


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = ('title', 'hash_link', 'time_create', 'user')


class LinkSerializer(Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    user = serializers.IntegerField()
    expiration = serializers.IntegerField(default=None)
    key_for_s3 = serializers.UUIDField()
    availability = serializers.CharField()

    def create(self, validated_data):
        key_for_s3 = str(validated_data.get('key_for_s3'))

        key = caches['redis'].keys('hash_key: *')[0]
        hash_link = caches['redis'].get(key)
        caches['redis'].delete(key)

        if validated_data.get('expiration'):
            expiration = timezone.localtime() + timedelta(seconds=validated_data.get('expiration'))
        else:
            expiration = None

        data = {
            'title': validated_data.get('title'),
            'user': User.objects.get(id=validated_data.get('user')),
            'hash_link': hash_link,
            'expiration': expiration,
            'availability': validated_data.get('availability'),
            'key_for_s3': key_for_s3,
        }

        s3_storage.create_or_update_object(content=validated_data.get('content'),
                                           key_for_s3=key_for_s3,
                                           ex=expiration)

        return Note.objects.create(**data)

    def update(self, instance, validated_data):
        if not validated_data.get('expiration'):  # for patch method
            expiration = instance.expiration
        else:
            expiration = timezone.localtime() + timedelta(seconds=validated_data.get('expiration'))

        key_for_s3 = str(instance.key_for_s3)
        content = validated_data.get('content', False)

        s3_storage.create_or_update_object(content=content,
                                           key_for_s3=key_for_s3,
                                           ex=expiration)

        instance.title = validated_data.get('title', instance.title)
        instance.availability = validated_data.get('availability', instance.availability)
        instance.expiration = expiration
        instance.save()

        return instance
