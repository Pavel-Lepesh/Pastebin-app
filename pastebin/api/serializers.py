from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Note
from .s3_storage import generate_link
from django.contrib.auth.models import User
from django.core.cache import caches


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title', 'hash_link', 'time_create', 'user')


class LinkSerializer(Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    user = serializers.IntegerField()
    expiration = serializers.IntegerField(default=3600)

    def create(self, validated_data):
        key = caches['redis'].keys('hash_key: *')[0]
        hash_link = caches['redis'].get(key)
        caches['redis'].delete(key)

        data = {
            'title': validated_data.get('title'),
            'link': generate_link(validated_data.get('content'),
                                  expiration=validated_data.get('expiration')),
            'user': User.objects.get(id=validated_data.get('user')),
            'hash_link': hash_link
        }

        return Note.objects.create(**data)

    # def create(self, validated_data):
    #     hash_count = redis_deck.lpop('hash_deck').decode('utf-8')
    #
    #     data = {
    #         'title': validated_data.get('title'),
    #         'link': generate_link(validated_data.get('content'),
    #                               expiration=validated_data.get('expiration')),
    #         'user': User.objects.get(id=validated_data.get('user')),
    #         'hash_link': caches['redis'].get(hash_count)
    #     }
    #
    #     return Note.objects.create(**data)
