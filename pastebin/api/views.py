from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import mixins, status
from rest_framework.decorators import action
from accounts.models import User
from django.core.cache import cache, caches
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema
from .serializers import (NoteSerializer, LinkSerializer, CommentSerializer, GetCommentsSerializer)
from .doc_decorators import (comments_doc, note_meta_doc, users_stars_doc, notes_doc, url_note_doc,
                             recent_post_doc)
from .doc_serializers import NotFound404Serializer
from .models import Note, UserStars, UserCommentRating, UserLikes
from .s3_storage import s3_storage
from .permissions import IsOwnerOrReadOnly, IsOwnerOrReadOnlyComments
from botocore.exceptions import ClientError
import uuid
import logging

logger = logging.getLogger(__name__)


@extend_schema(tags=['Base access'])
@recent_post_doc
class RecentPosts(GenericViewSet,
                  mixins.ListModelMixin):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def list(self, request, *args, **kwargs):
        limit = kwargs['limit']
        notes = self.get_queryset().filter(availability='public').order_by('-time_create')[:limit]
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['User stars'])
@users_stars_doc
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
            return Response({'detail': 'This note is already in your collection'},
                            status=status.HTTP_400_BAD_REQUEST)

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


@extend_schema(tags=['Meta data'])
@note_meta_doc
class LikePost(GenericViewSet):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self):
        item = get_object_or_404(self.get_queryset(), hash_link=self.kwargs['hash_link'])
        return item

    def retrieve(self, request, hash_link):
        item = self.get_object()
        meta_data = {'views': item.meta_data.views,
                     'stars': item.meta_data.stars,
                     'likes': item.meta_data.likes}
        return Response(meta_data)

    @action(detail=True, methods=['post'])
    def like(self, request, hash_link):
        item = self.get_object()
        user_like = UserLikes.objects.filter(note=item, user=request.user)

        if user_like.exists():
            return Response({'detail': 'You have already liked the note'},
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
            return Response({'detail': 'You have\'t liked the note yet'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            item.meta_data.likes -= 1
            item.meta_data.save()
            user_like.delete()
            return Response({'likes': item.meta_data.likes})


@extend_schema(tags=['Base access'])
@url_note_doc
class URLNoteAPIView(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Note.objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'hash_link'

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), hash_link=self.kwargs['hash_link'])
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        item = self.get_object()
        item.meta_data.views += 1

        if item.meta_data.views >= 10:
            has_key = cache.has_key(item.hash_link)
            if not has_key:
                content = s3_storage.get_object_content(str(item.key_for_s3))
                cache.set(item.hash_link,
                          content,
                          300)
            content = cache.get(item.hash_link)
        else:
            content = s3_storage.get_object_content(str(item.key_for_s3))

        item.meta_data.save()
        return Response({'content': content})

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = LinkSerializer(instance=item, data={'user': item.user.id,
                                                         'key_for_s3': item.key_for_s3,
                                                         'hash_link': item.hash_link,
                                                         **request.data})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if cache.has_key(item.hash_link):
            cache.set(item.hash_link, request.data['content'])
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = LinkSerializer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if cache.has_key(item.hash_link):
            cache.set(item.hash_link, request.data['content'])
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        key_for_s3 = str(item.key_for_s3)
        s3_storage.delete_object(key_for_s3)

        if cache.has_key(item.hash_link):
            cache.delete(item.hash_link)

        self.perform_destroy(item)

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['User notes'])
@notes_doc
class LinkAPIView(GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin):
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = (IsAuthenticated,)
    serializer_class = NoteSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        elif self.action == 'public':
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = Note.objects.filter(user=request.user.id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(  # documenting here because there is an error in the library
        summary='return a list of public user\'s notes',
        responses={
            status.HTTP_200_OK: NoteSerializer(many=True),
            status.HTTP_404_NOT_FOUND: NotFound404Serializer
        }
    )
    def public(self, request, user_id):
        user = get_object_or_404(User.objects.all(), id=user_id)
        public_notes = Note.objects.filter(user=user.id, availability='public')
        serializer = self.get_serializer(public_notes, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        limit_kb = 10 * 1024

        if len(request.data['content'].encode('utf-8')) > limit_kb:
            return Response('Content data is too big.', status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        key_for_s3 = str(uuid.uuid4())

        while s3_storage.object_exist(key_for_s3):
            key_for_s3 = str(uuid.uuid4())

        while True:
            try:
                key = caches['redis'].keys('hash_key: *')[0]
                hash_link = caches['redis'].get(key)
                caches['redis'].delete(key)
                serializer = LinkSerializer(data={'user': request.user.id,
                                                  'key_for_s3': key_for_s3,
                                                  'hash_link': hash_link,
                                                  **request.data})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                break
            except IntegrityError:
                continue  # this error catches hash_link collisions
            except ClientError as error:
                # continue
                return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


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
