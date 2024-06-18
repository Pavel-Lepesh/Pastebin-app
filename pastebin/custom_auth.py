import os

from accounts.models import User
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from jose import JWTError, jwt
from rest_framework import authentication, exceptions, status
from rest_framework.response import Response

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
