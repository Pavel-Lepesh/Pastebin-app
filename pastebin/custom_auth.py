from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from accounts.models import User
from rest_framework import authentication
import requests


class SettingsBackend(authentication.BaseAuthentication):
    def authenticate(self, request):
        print("Check")
        if request.headers.get("Authorization", None):
            user = User.objects.get(id=13)
            return user, True
        else:
            return None
