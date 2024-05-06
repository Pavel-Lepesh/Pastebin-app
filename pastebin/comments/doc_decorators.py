from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import status
from .serializers import CommentSerializer
from doc_serializers import *


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
