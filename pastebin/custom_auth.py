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
        token = request.headers.get("Authorization", None)
        print(request.headers)
        if token:
            try:
                payload = jwt.decode(token[7:], os.getenv("JWT_ACCESS_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
                user_id, is_superuser, exp = payload["user_id"], payload["is_superuser"], payload["exp"]
                user = get_object_or_404(User.objects.all(), id=user_id)
                return user, None
            except JWTError as error:
                print(f"Token from main with error {token}")
                raise exceptions.AuthenticationFailed({"JWT error": error})
        else:
            return None
