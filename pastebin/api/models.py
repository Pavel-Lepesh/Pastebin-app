from django.db import models
from django.contrib.auth.models import User


class NoteMetaData(models.Model):
    views = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)


class Note(models.Model):
    title = models.CharField(max_length=255)
    hash_link = models.CharField(max_length=200, db_index=True, unique=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, verbose_name='username', on_delete=models.CASCADE)
    key_for_s3 = models.UUIDField()
    availability = models.CharField(choices=(('public', 'public'),
                                             ('private', 'private')))
    meta_data = models.OneToOneField(NoteMetaData, on_delete=models.CASCADE)
    user_stars = models.ManyToManyField(User, through='UserStars', related_name='starred_notes')

    def __str__(self):
        return self.title


class UserStars(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'note')


class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    body = models.TextField()

    def __str__(self):
        return f'By {self.user.username}'

    class Meta:
        ordering = ['created']
