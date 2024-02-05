from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import UserSerializer
from .doc_serializers import BadRequest400Serializer
from rest_framework import status


def account_doc(cls):
    return extend_schema_view(
        post=extend_schema(
            summary='create a new user',
            request=UserSerializer,
            responses={
                status.HTTP_201_CREATED: UserSerializer,
                status.HTTP_400_BAD_REQUEST: BadRequest400Serializer
            }
        )
    )(cls)
