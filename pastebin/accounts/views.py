from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer, AllUsersSerializer
from .doc_decorators import account_doc, delete_account_doc
from .models import User


@extend_schema(tags=['Accounts'])
@account_doc
class UserCreateAPI(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            return response
        except Exception as error:
            return Response({"error": error}, status=400)


@extend_schema(tags=['Accounts'])
@delete_account_doc
class UserDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        User.objects.filter(email=request.user.email).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def get_me(request):
    h = request.headers
    return Response({"user": str(request.user)})


@api_view(["GET"])
def get_all_users(request):
    users = User.objects.all()
    serializer = AllUsersSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_user(request, user_id):
    User.objects.filter(id=user_id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
