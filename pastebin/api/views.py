from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework import mixins, status
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema
from .serializers import NoteSerializer, LinkSerializer
from .models import Note
from .s3_storage import s3_storage
from botocore.exceptions import ClientError
import uuid


class URLNoteAPIView(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    queryset = Note.objects.all()
    parser_classes = (MultiPartParser, JSONParser)

    def retrieve(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), hash_link=kwargs['pk'])
        content = s3_storage.get_object_content(str(item.key_for_s3))
        return Response({'content': content})

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), hash_link=kwargs['pk'])
        serializer = LinkSerializer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'data': serializer.validated_data})

    def destroy(self, request, pk=None):
        item = get_object_or_404(self.get_queryset(), hash_link=pk)
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
        return Response({'data': serializer.data, 'user': request.user.id})

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
            except (IntegrityError, ClientError):
                # возможно стоит поставить лог
                continue

        return Response({'data': serializer.validated_data})
