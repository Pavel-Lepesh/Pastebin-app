from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Comment


class FilterReviewListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class GetCommentsSerializer(ModelSerializer):
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Comment
        fields = ('id', 'note', 'user', 'body', 'children')


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'note', 'user', 'body', 'parent')
