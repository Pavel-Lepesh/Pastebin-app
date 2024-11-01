import os
import uuid

import requests
from accounts.models import User
from botocore.exceptions import ClientError
from django.core.cache import cache
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from doc_serializers import NotFound404Serializer
from drf_spectacular.utils import extend_schema
from hash_generator_connection import hash_generator
from kafka.errors import KafkaError
from loguru import logger
from permissions import IsOwnerOrReadOnly, IsOwnerOrReadOnlyPublic
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from s3_storage import s3_storage

from .doc_decorators import (note_meta_doc, notes_doc, recent_post_doc,
                             url_note_doc)
from .kafka_producer import kafka_producer
from .models import Note, PrivateLink, UserLikes
from .serializers import LinkSerializer, NoteSerializer


@extend_schema(tags=['User notes'])
class PrivateLinkAPI(GenericViewSet):
    queryset = Note.objects.all()
    permission_classes = [IsOwnerOrReadOnly,]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), hash_link=self.kwargs['hash_link'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, private_link):
        obj = get_object_or_404(PrivateLink.objects.all(), private_link=private_link)
        content = s3_storage.get_object_content(str(obj.note.key_for_s3))
        return Response({"content": content})

    def post(self, request, hash_link):
        try:
            note = self.get_object()

            while True:
                private_link = uuid.uuid4()
                objs = PrivateLink.objects.filter(private_link=private_link)
                if not objs.exists():
                    break

            PrivateLink.objects.create(private_link=private_link, note=note)
            return Response({"private_link": private_link})
        except IntegrityError:
            obj = PrivateLink.objects.filter(note=note.id)
            return Response({"private_link": obj[0].private_link})

    def delete(self, request, private_link):
        obj = get_object_or_404(
            PrivateLink.objects.all(),
            private_link=private_link
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (IsOwnerOrReadOnlyPublic,)
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

        response_search_service = requests.put(
            f"http://{os.getenv('SEARCH_HOST')}:{os.getenv('SEARCH_PORT')}/v1/search/update_doc/{item.hash_link}?title={request.data['title']}"
        )
        if response_search_service.status_code == 201:
            self.perform_update(serializer)
            logger.info(f"Document {item.hash_link} updated successfully")
        elif response_search_service.status_code == 404:
            logger.error(f"Document {item.hash_link} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            logger.error(f"Error during handling document {item.hash_link}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if cache.has_key(item.hash_link):
            cache.set(item.hash_link, request.data['content'])
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = LinkSerializer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        response_search_service = requests.put(
            f"http://{os.getenv('SEARCH_HOST')}:{os.getenv('SEARCH_PORT')}/v1/search/update_doc/{item.hash_link}?title={request.data['title']}"
        )

        if response_search_service.status_code == 201:
            self.perform_update(serializer)
            logger.info(f"Document {item.hash_link} updated successfully")
        elif response_search_service.status_code == 404:
            logger.error(f"Document {item.hash_link} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            logger.error(f"Error during handling document {item.hash_link}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if cache.has_key(item.hash_link):
            cache.set(item.hash_link, request.data['content'])
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            key_for_s3 = str(item.key_for_s3)
            s3_storage.delete_object(key_for_s3)

            if cache.has_key(item.hash_link):
                cache.delete(item.hash_link)

            response_search_service = requests.delete(
                f"http://{os.getenv('SEARCH_HOST')}:{os.getenv('SEARCH_PORT')}/v1/search/delete_doc/{item.hash_link}"
            )

            if response_search_service.status_code == 204:
                self.perform_destroy(item)
                logger.info(f"Note {item.hash_link} deleted correctly")
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                logger.info("Error was occurred during deleting a note")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as error:
            logger.error(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        attempts_limit = 10

        if len(request.data['content'].encode('utf-8')) > limit_kb:
            return Response('Content data is too big.', status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        key_for_s3 = str(uuid.uuid4())

        while s3_storage.object_exist(key_for_s3):
            key_for_s3 = str(uuid.uuid4())

        for attempt in range(attempts_limit):
            try:
                hash_link = hash_generator.get_hash()
                serializer = LinkSerializer(data={'user': request.user.id,
                                                  'key_for_s3': key_for_s3,
                                                  'hash_link': hash_link,
                                                  **request.data})
                serializer.is_valid(raise_exception=True)
                kafka_producer.send_note(title=request.data["title"], hash_link=hash_link)

                serializer.save()
                break
            except IntegrityError:  # this error catches hash_link collisions
                if attempt == attempts_limit - 1:
                    logger.error("Cannot reach unique hash value")
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                logger.warning("Reaching unique hash link failed. Launching new attempt...")
                continue
            except (ClientError, KafkaError) as error:
                logger.error(error)
                return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as error:
                logger.error(f"Unexpected error: {error}")
                return Response({"unexpected error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
