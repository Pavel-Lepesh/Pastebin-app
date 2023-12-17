from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework import mixins, status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema
from .serializers import NoteSerializer, LinkSerializer
from .models import Note, UserStars
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
            userstar = self.queryset.create(user_id=request.user.id, note_id=item.id)
            userstar.save()
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

        if item.meta_data:
            item.meta_data.delete()

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
        request.data._mutable = True  # для того чтобы можно было изменять данные
        request.data.update({'user': request.user.id})
        key_for_s3 = str(uuid.uuid4())

        while s3_storage.object_exist(key_for_s3):
            key_for_s3 = str(uuid.uuid4())
        request.data.update({'key_for_s3': key_for_s3})

        while True:
            try:
                serializer = LinkSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                break
            except (IntegrityError, ClientError) as error:
                print(error)
                continue

        return Response({'data': serializer.validated_data})
