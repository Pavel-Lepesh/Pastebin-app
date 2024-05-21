from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer
from .doc_decorators import account_doc, delete_account_doc
from .models import User
import requests


@extend_schema(tags=['Accounts'])
@account_doc
class UserCreateAPI(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    def post(self, request, *args, **kwargs):
        data = {
            "username": request.data["username"],
            "password": request.data["password"],
            "email": request.data["email"]
        }
        try:
            post_user = requests.post(url="http://localhost:80/v1/users/create", json=data)
        except requests.exceptions.ConnectionError as error:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(f"{post_user.content}", status=post_user.status_code)


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
    print(request.user.id)
    return Response({"user": 1})
