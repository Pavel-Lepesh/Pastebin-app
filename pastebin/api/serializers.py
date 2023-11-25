from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Note
from .s3_storage import generate_link
from django.contrib.auth.models import User
from django.core.cache import cache


hash_count = 0


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
        global hash_count

        data = {
            'title': validated_data.get('title'),
            'link': generate_link(validated_data.get('content'),
                                  expiration=validated_data.get('expiration')),
            'user': User.objects.get(id=validated_data.get('user')),
            'hash_link': cache.get(str(hash_count))
        }

        hash_count += 1

        return Note.objects.create(**data)
