from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer
from .doc_decorators import account_doc


@extend_schema(tags=['Accounts'])
@account_doc
class UserCreateAPI(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
