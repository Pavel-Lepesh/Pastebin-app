from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.core.cache import cache
#from django.utils.decorators import method_decorator
#from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from .serializers import NoteSerializer, LinkSerializer
from .models import Note
import requests


class RetrieveKey(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        item = cache.get(pk)
        return Response({'get': item})


class RetrieveNoteAPIView(RetrieveAPIView):
    queryset = Note.objects.all()

    def retrieve(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), hash_link=kwargs['pk'])
        content = requests.get(item.link).text

        return Response({'content': content})


class NoteAPIView(ReadOnlyModelViewSet):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()


class LinkAPIView(ViewSet):
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @extend_schema(request=NoteSerializer, responses=NoteSerializer)
    #@method_decorator(cache_page(600))
    def list(self, request):
        queryset = Note.objects.filter(user=request.user.id)
        serializer = NoteSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=NoteSerializer, responses=NoteSerializer)
    #@method_decorator(cache_page(300))
    def retrieve(self, request, pk=None):
        queryset = Note.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = NoteSerializer(item)
        return Response(serializer.data)

    @extend_schema(request=LinkSerializer, responses=LinkSerializer)
    def create(self, request):
        request.data._mutable = True
        request.data.update({'user': request.user.id})
        serializer = LinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)

    @extend_schema(responses=NoteSerializer)
    def destroy(self, request, pk=None):
        queryset = Note.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = NoteSerializer(item)
        item.delete()
        return Response({'delete': serializer.data})
