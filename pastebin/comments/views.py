from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from loguru import logger
from notes.models import Note
from permissions import IsOwnerOrReadOnlyComments
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .doc_decorators import comments_doc
from .models import UserCommentRating
from .serializers import CommentSerializer, GetCommentsSerializer


@extend_schema(tags=['Comments'])
@comments_doc
class NoteComments(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Note.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnlyComments,)

    def get_object(self):
        note = get_object_or_404(self.get_queryset(), hash_link=self.kwargs['hash_link'])
        obj = get_object_or_404(note.comments, id=self.kwargs['note_comment_id'])
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        note = get_object_or_404(self.get_queryset(), hash_link=kwargs['hash_link'])
        serializer = GetCommentsSerializer(note.comments.all(), many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        note = get_object_or_404(self.get_queryset(), hash_link=kwargs['hash_link'])
        serializer = self.get_serializer(data={'note': note.id,
                                               'user': request.user.id,
                                               **request.data})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(instance=comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        self.perform_destroy(comment)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def rating(self, request, hash_link=None, note_comment_id=None, action_=None, cancel=None):
        try:
            comment = self.get_object()
            user_rating = UserCommentRating.objects.filter(user=request.user, comment=comment)

            if not cancel:
                if user_rating.exists():
                    return Response({'detail': 'You have already rated the comment'},
                                    status=status.HTTP_400_BAD_REQUEST)
                match action_:
                    case 'like':
                        comment.meta_data.likes += 1
                    case 'dislike':
                        comment.meta_data.dislikes += 1
                UserCommentRating.objects.create(user=request.user,
                                                 comment=comment,
                                                 rating=action_)
            else:
                if not user_rating.exists():
                    return Response({'detail': 'You have\'t rated the comment yet'},
                                    status=status.HTTP_400_BAD_REQUEST)

                accurate_rating: str = get_object_or_404(user_rating, user=request.user, comment=comment).rating
                if accurate_rating != action_:
                    return Response({'detail': 'You cannot cancel a rating you did not give'},
                                    status=status.HTTP_400_BAD_REQUEST)

                match action_:
                    case 'like':
                        comment.meta_data.likes -= 1
                    case 'dislike':
                        comment.meta_data.dislikes -= 1
                user_rating.delete()

            comment.meta_data.save()
            return Response({'likes': comment.meta_data.likes,
                             'dislikes': comment.meta_data.dislikes})
        except Exception as error:
            logger.error(error)
