from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import mixins, status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .serializers import (NoteSerializer, LinkSerializer, CommentSerializer)
from .doc_serializers import (GetCommentSerializer, NotFound404Serializer, NotAuthorized401Serializer,
                              PostOrUpdateCommentSerializer, BadRequest400Serializer, Forbidden403Serializer,
                              RateCommentSerializer, CommonBadRequest400Serializer)
from .models import Note, UserStars, UserCommentRating, UserLikes
from .s3_storage import s3_storage
from .permissions import IsOwnerOrReadOnly, IsOwnerOrReadOnlyComments
from botocore.exceptions import ClientError
import uuid


class UserStars(mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                mixins.CreateModelMixin,
                GenericViewSet):
    queryset = UserStars.objects.all()
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        stars = {str(star): star.hash_link for star in user.starred_notes.all()}
        return Response({'my_stars': stars})

    def create(self, request, *args, **kwargs):
        item = get_object_or_404(Note.objects.all(), hash_link=kwargs['hash_link'])

        try:
            self.queryset.create(user_id=request.user.id, note_id=item.id)
        except IntegrityError as error:
            return Response({'message': 'This note is already in your collection'},
                            status=status.HTTP_409_CONFLICT)

        item.meta_data.stars += 1
        item.meta_data.save()

        return Response({'save_to_stars': str(item)}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        note = get_object_or_404(Note.objects.all(), hash_link=kwargs['hash_link'])
        item = get_object_or_404(self.get_queryset(),
                                 user_id=request.user.id,
                                 note_id=note.id)
        item.delete()

        note.meta_data.stars -= 1
        note.meta_data.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikePost(GenericViewSet):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self):
        item = get_object_or_404(self.get_queryset(), hash_link=self.kwargs['hash_link'])
        return item

    def retrieve(self, request, hash_link):
        item = self.get_object()
        meta_data = {'views': item.meta_data.views,
                     'likes': item.meta_data.likes,
                     'stars': item.meta_data.stars}
        return Response(meta_data)

    @action(detail=True, methods=['post'])
    def like(self, request, hash_link):
        item = self.get_object()
        user_like = UserLikes.objects.filter(note=item, user=request.user)

        if user_like.exists():
            return Response({'message': 'You have already liked the note'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            item.meta_data.likes += 1
            item.meta_data.save()
            UserLikes.objects.create(note=item, user=request.user, like=True)
            return Response({'likes': item.meta_data.likes})

    @action(detail=True, methods=['post'])
    def cancel_like(self, request, hash_link):
        item = self.get_object()
        user_like = UserLikes.objects.filter(note=item, user=request.user)

        if not user_like.exists():
            return Response({'message': 'You have\'t liked the note yet'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            item.meta_data.likes -= 1
            item.meta_data.save()
            user_like.delete()
            return Response({'likes': item.meta_data.likes})


class URLNoteAPIView(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Note.objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = (IsOwnerOrReadOnly,)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), hash_link=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        item = self.get_object()
        item.meta_data.views += 1

        if item.meta_data.views >= 10:
            content = cache.get(item.hash_link)
            if not content:
                content = s3_storage.get_object_content(str(item.key_for_s3))
                cache.set(item.hash_link,
                          content,
                          300)
        else:
            content = s3_storage.get_object_content(str(item.key_for_s3))

        item.meta_data.save()
        return Response({'content': content})

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = LinkSerializer(instance=item, data={'user': item.user.id,
                                                         'key_for_s3': item.key_for_s3,
                                                         **request.data})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'data': serializer.validated_data})

    def partial_update(self, request, *args, **kwargs):
        serializer = LinkSerializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'data': serializer.validated_data})

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        key_for_s3 = str(item.key_for_s3)
        s3_storage.delete_object(key_for_s3)

        if cache.get(item.hash_link):
            cache.delete(item.hash_link)

        self.perform_destroy(item)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LinkAPIView(ViewSet):
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        elif self.action == 'public_notes':
            return [AllowAny()]
        return super().get_permissions()

    #@extend_schema(request=NoteSerializer, responses=NoteSerializer)
    def list(self, request):
        queryset = Note.objects.filter(user=request.user.id)
        serializer = NoteSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def public_notes(self, request, user_id):
        public_notes = Note.objects.filter(user=user_id, availability='public')
        serializer = NoteSerializer(public_notes, many=True)
        return Response({'data': serializer.data})

    #@extend_schema(request=LinkSerializer, responses=LinkSerializer)
    def create(self, request):
        limit_kb = 10 * 1024

        if len(request.data['content'].encode('utf-8')) > limit_kb:
            return Response('Content data is too big.', status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        key_for_s3 = str(uuid.uuid4())

        while s3_storage.object_exist(key_for_s3):
            key_for_s3 = str(uuid.uuid4())

        while True:
            try:
                serializer = LinkSerializer(data={'user': request.user.id,
                                                  'key_for_s3': key_for_s3,
                                                  **request.data})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                break
            except (IntegrityError, ClientError) as error:
                print(error)
                continue

        return Response({'data': serializer.validated_data})


@extend_schema(tags=['Comments'])
@extend_schema_view(
    list=extend_schema(
        summary='get note\'s comments',
        responses={
            status.HTTP_200_OK: GetCommentSerializer(many=True),
            status.HTTP_404_NOT_FOUND: NotFound404Serializer,
        }
    ),
    create=extend_schema(
        summary='post a comment for the note',
        request=PostOrUpdateCommentSerializer,
        responses={
            status.HTTP_201_CREATED: CommentSerializer,
            status.HTTP_400_BAD_REQUEST: BadRequest400Serializer(many=True),
            status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
        }
    ),
    partial_update=extend_schema(
        summary='update comment\'s body',
        request=PostOrUpdateCommentSerializer,
        responses={
            status.HTTP_201_CREATED: CommentSerializer,
            status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
            status.HTTP_403_FORBIDDEN: Forbidden403Serializer
        }
    ),
    destroy=extend_schema(
        summary='delete the comment',
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_403_FORBIDDEN: Forbidden403Serializer,
            status.HTTP_404_NOT_FOUND: NotFound404Serializer
        }
    ),
    rating=extend_schema(
        summary='rate the comment',
        request=None,
        responses={
            status.HTTP_200_OK: RateCommentSerializer,
            status.HTTP_400_BAD_REQUEST: CommonBadRequest400Serializer,
            status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
            status.HTTP_404_NOT_FOUND: NotFound404Serializer
        },
        parameters=[
            OpenApiParameter(
                name='action_',
                description='Select "like" or "dislike" to rate the comment.',
                location=OpenApiParameter.PATH,
                enum=['like', 'dislike']
            ),
            OpenApiParameter(
                name='cancel',
                description='If you want to cancel an already existing rate, type "cancel" at the end of the endpoint.'
                            'Otherwise, leave this field blank.',
                required=False,
                location=OpenApiParameter.PATH,
                enum=['cancel', '']
            )
        ]
    )
)
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
        obj = get_object_or_404(note.comments, note_comment_id=self.kwargs['note_comment_id'])
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        note = get_object_or_404(self.get_queryset(), hash_link=kwargs['hash_link'])
        comments = [{'note_comment_id': comment.note_comment_id,
                     'user': str(comment),
                     'body': comment.body,
                     'likes': comment.meta_data.likes,
                     'dislikes': comment.meta_data.dislikes,
                     'created': comment.created} for comment in note.comments.all()]
        return Response({'comments': comments})

    def create(self, request, *args, **kwargs):
        note = get_object_or_404(self.get_queryset(), hash_link=kwargs['hash_link'])
        note_comment_id = note.comments.count() + 1
        serializer = self.get_serializer(data={'note': note.id,
                                               'user': request.user.id,
                                               'note_comment_id': note_comment_id,
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
        note = get_object_or_404(self.get_queryset(), hash_link=hash_link)
        comment = get_object_or_404(note.comments, note_comment_id=note_comment_id)
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
            match action_:
                case 'like':
                    comment.meta_data.likes -= 1
                case 'dislike':
                    comment.meta_data.dislikes -= 1
            user_rating.delete()

        comment.meta_data.save()
        return Response({'likes': comment.meta_data.likes,
                         'dislikes': comment.meta_data.dislikes})
