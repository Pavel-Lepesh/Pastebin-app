from doc_serializers import *
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status

from .serializers import LinkSerializer, NoteSerializer


def recent_post_doc(cls):
    return extend_schema_view(
        list=extend_schema(
            summary='get recent posts',
            responses={
                status.HTTP_200_OK: NoteSerializer(many=True)
            }
        )
    )(cls)


def note_meta_doc(cls):
    return extend_schema_view(
        retrieve=extend_schema(
            summary='get note\'s metadata',
            responses={
                status.HTTP_200_OK: NoteMetaDataSerializer,
                status.HTTP_404_NOT_FOUND: NotFound404Serializer
            }
        ),
        like=extend_schema(
            summary='like the note',
            responses={
                status.HTTP_200_OK: NoteLikesSerializer,
                status.HTTP_400_BAD_REQUEST: CommonBadRequest400Serializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
            }
        ),
        cancel_like=extend_schema(
            summary='cancel your like for the note',
            responses={
                status.HTTP_200_OK: NoteLikesSerializer,
                status.HTTP_400_BAD_REQUEST: CommonBadRequest400Serializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
            }
        )
    )(cls)


def notes_doc(cls):
    return extend_schema_view(
        list=extend_schema(
            summary='returns a list of your notes',
            responses={
                status.HTTP_200_OK: NoteSerializer(many=True),
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
            }
        ),
        create=extend_schema(
            summary='create a note',
            request=CreateNoteSerializer,
            responses={
                status.HTTP_201_CREATED: LinkSerializer,
                status.HTTP_400_BAD_REQUEST: BadRequest400Serializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
            }
        ),
    )(cls)


def url_note_doc(cls):
    return extend_schema_view(
        retrieve=extend_schema(
            summary='get the note',
            responses={
                status.HTTP_200_OK: BaseNoteSerializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
                status.HTTP_403_FORBIDDEN: Forbidden403Serializer,
                status.HTTP_404_NOT_FOUND: NotFound404Serializer
            }
        ),
        update=extend_schema(
            summary='update your note',
            request=CreateNoteSerializer,
            responses={
                status.HTTP_201_CREATED: LinkSerializer,
                status.HTTP_400_BAD_REQUEST: BadRequest400Serializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
                status.HTTP_403_FORBIDDEN: Forbidden403Serializer
            }
        ),
        partial_update=extend_schema(
            summary='partially update your note',
            request=CreateNoteSerializer(partial=True),
            responses={
                status.HTTP_201_CREATED: UpdateNoteSerializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
                status.HTTP_403_FORBIDDEN: Forbidden403Serializer
            }
        ),
        destroy=extend_schema(
            summary='delete your note',
            responses={
                status.HTTP_204_NO_CONTENT: None,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
                status.HTTP_403_FORBIDDEN: Forbidden403Serializer
            }
        )
    )(cls)
