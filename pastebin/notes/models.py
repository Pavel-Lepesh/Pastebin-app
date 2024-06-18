from django.conf import settings
from django.db import models


class UserStars(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'note')


class Note(models.Model):
    title = models.CharField(max_length=255)
    hash_link = models.CharField(max_length=200, db_index=True, unique=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='username', on_delete=models.CASCADE)
    key_for_s3 = models.UUIDField()
    availability = models.CharField(choices=(('public', 'public'),
                                             ('private', 'private')),
                                    default='public')
    user_stars = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserStars', related_name='starred_notes')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class NoteMetaData(models.Model):
    note = models.OneToOneField(Note, on_delete=models.CASCADE, related_name='meta_data')
    views = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)


class UserLikes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'note')
