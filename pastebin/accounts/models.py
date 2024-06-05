from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.IntegerField(primary_key=True, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
