from doc_serializers import *
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status


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
