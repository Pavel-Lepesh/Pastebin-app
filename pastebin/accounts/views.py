from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer
from .doc_decorators import account_doc, delete_account_doc
from .models import User


@extend_schema(tags=['Accounts'])
@account_doc
class UserCreateAPI(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Accounts'])
@delete_account_doc
class UserDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        User.objects.filter(email=request.user.email).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
