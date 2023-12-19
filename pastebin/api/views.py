from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework import mixins, status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema
from .serializers import NoteSerializer, LinkSerializer, CommentSerializer
from .models import Note, UserStars, Comment, UserCommentRating
from .s3_storage import s3_storage
from botocore.exceptions import ClientError
import uuid


class UserStars(mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                mixins.CreateModelMixin,
                GenericViewSet):
    queryset = UserStars.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        stars = {str(star): star.hash_link for star in user.starred_notes.all()}
        return Response({'my_stars': stars})

    def create(self, request, *args, **kwargs):
        item = get_object_or_404(Note.objects.all(), hash_link=kwargs['hash_link'])

        try:
            self.queryset.create(user_id=request.user.id, note_id=item.id)
        except IntegrityError as error:
            return Response({'message': 'This star is already in your collection'},
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


class LikePost(GenericAPIView):
    queryset = Note.objects.all()

    def post(self, request, hash_link):
        item = get_object_or_404(self.get_queryset(), hash_link=hash_link)
        item.meta_data.likes += 1
        item.meta_data.save()
        return Response({'likes': item.meta_data.likes})


class URLNoteAPIView(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Note.objects.all()
    parser_classes = (MultiPartParser, JSONParser)

    def retrieve(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), hash_link=kwargs['pk'])
        item.meta_data.views += 1
        item.meta_data.save()
        content = s3_storage.get_object_content(str(item.key_for_s3))
        return Response({'content': content})

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), hash_link=kwargs['pk'])
        serializer = LinkSerializer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'data': serializer.validated_data})

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), hash_link=kwargs['pk'])
        key_for_s3 = str(item.key_for_s3)
        s3_storage.delete_object(key_for_s3)
        self.perform_destroy(item)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LinkAPIView(ViewSet):
    parser_classes = (MultiPartParser, JSONParser)
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)

    @extend_schema(request=NoteSerializer, responses=NoteSerializer)
    def list(self, request):
        queryset = Note.objects.filter(user=request.user.id)
        serializer = NoteSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    #@extend_schema(request=LinkSerializer, responses=LinkSerializer)
    def create(self, request):
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


class NoteComments(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Note.objects.all()
    serializer_class = CommentSerializer

    def list(self, request, *args, **kwargs):
        note = get_object_or_404(self.get_queryset(), hash_link=kwargs['hash_link'])
        comments = [{'note_comment_id': comment.note_comment_id,
                     'user': str(comment),
                     'body': comment.body,
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

    def destroy(self, request, *args, **kwargs):
        note = get_object_or_404(self.get_queryset(), hash_link=kwargs['hash_link'])
        comment = get_object_or_404(note.comments, note_comment_id=kwargs['note_comment_id'])
        self.perform_destroy(comment)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def rating(self, request, hash_link=None, note_comment_id=None, action_=None, cancel=None):
        note = get_object_or_404(self.get_queryset(), hash_link=hash_link)
        comment = get_object_or_404(note.comments, note_comment_id=note_comment_id)
        user_rating = UserCommentRating.objects.filter(user=request.user, comment=comment)

        if not cancel:
            if user_rating.exists():
                return Response({'message': 'You have already rated the comment'},
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
                return Response({'message': 'You have\'t rated the comment yet'},
                                status=status.HTTP_400_BAD_REQUEST)
            match action_:
                case 'like':
                    comment.meta_data.likes -= 1
                case 'dislike':
                    comment.meta_data.dislikes -= 1
            user_rating.delete()

        comment.meta_data.save()
        return Response({'rating': {'likes': comment.meta_data.likes,
                                    'dislikes': comment.meta_data.dislikes}})
