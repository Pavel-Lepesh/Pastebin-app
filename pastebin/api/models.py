from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    title = models.CharField(max_length=255)
    hash_link = models.CharField(max_length=200, db_index=True, unique=True)
    link = models.URLField(max_length=200)
    time_create = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, verbose_name='username', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    