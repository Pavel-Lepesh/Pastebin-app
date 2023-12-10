from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    title = models.CharField(max_length=255)
    hash_link = models.CharField(max_length=200, db_index=True, unique=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, verbose_name='username', on_delete=models.CASCADE)
    key_for_s3 = models.UUIDField()

    def __str__(self):
        return self.title
    