from rest_framework import authentication, status, exceptions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from jose import jwt, JWTError
from dotenv import load_dotenv
from accounts.models import User
import os


load_dotenv()


class SettingsBackend(authentication.BaseAuthentication):
    def authenticate(self, request):
        print("Check")
        token = request.headers.get("Authorization", None)
        if token:
            try:
                print(os.getenv("JWT_ACCESS_SECRET_KEY"), os.getenv("JWT_ALGORITHM"))
                payload = jwt.decode(token[7:], os.getenv("JWT_ACCESS_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
                user_id, is_superuser, exp = payload["user_id"], payload["is_superuser"], payload["exp"]
                user = get_object_or_404(User.objects.all(), id=user_id)
                return user, None
            except JWTError as error:
                raise exceptions.AuthenticationFailed({"JWT error": error})
        else:
            return None
