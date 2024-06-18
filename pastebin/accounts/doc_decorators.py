from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status

from .doc_serializers import (BadRequest400Serializer,
                              NotAuthorized401Serializer)
from .serializers import UserSerializer


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


def delete_account_doc(cls):
    return extend_schema_view(
        delete=extend_schema(
            summary='delete your account',
            responses={
                status.HTTP_204_NO_CONTENT: None,
                status.HTTP_401_UNAUTHORIZED: NotAuthorized401Serializer
            }
        )
    )(cls)
