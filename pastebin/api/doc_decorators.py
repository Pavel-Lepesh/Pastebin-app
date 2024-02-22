from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import status
from .serializers import (NoteSerializer, LinkSerializer, CommentSerializer)
from .doc_serializers import (NotFound404Serializer, NotAuthorized401Serializer, PostCommentSerializer,
                              UpdateCommentSerializer, BadRequest400Serializer, Forbidden403Serializer,
                              RateCommentSerializer, CommonBadRequest400Serializer, NoteMetaDataSerializer,
                              NoteLikesSerializer, AddStarSerializer, MyStarsSerializer, CreateNoteSerializer,
                              BaseNoteSerializer, UpdateNoteSerializer, ListCommentsSerializer)


def recent_post_doc(cls):
    return extend_schema_view(
        list=extend_schema(
            summary='get recent posts',
            responses={
                status.HTTP_200_OK: NoteSerializer(many=True)
            }
        )
    )(cls)


def comments_doc(cls):
    return extend_schema_view(
        list=extend_schema(
            summary='get note\'s comments',
            responses={
                status.HTTP_200_OK: ListCommentsSerializer(many=True),
                status.HTTP_404_NOT_FOUND: NotFound404Serializer,
            }
        ),
        create=extend_schema(
            summary='post a comment for the note',
            request=PostCommentSerializer,
            responses={
                status.HTTP_201_CREATED: CommentSerializer,
                status.HTTP_400_BAD_REQUEST: BadRequest400Serializer(many=True),
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
            }
        ),
        partial_update=extend_schema(
            summary='update comment\'s body',
            request=UpdateCommentSerializer,
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


def users_stars_doc(cls):
    return extend_schema_view(
        create=extend_schema(
            summary='add the note to your stars',
            responses={
                status.HTTP_201_CREATED: AddStarSerializer,
                status.HTTP_400_BAD_REQUEST: CommonBadRequest400Serializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
                status.HTTP_404_NOT_FOUND: NotFound404Serializer
            }
        ),
        retrieve=extend_schema(
            summary='get a list of your starred notes',
            responses={
                status.HTTP_200_OK: MyStarsSerializer,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
            }
        ),
        destroy=extend_schema(
            summary='delete the note from your stars',
            responses={
                status.HTTP_204_NO_CONTENT: None,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer,
                status.HTTP_404_NOT_FOUND: NotFound404Serializer
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
