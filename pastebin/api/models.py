from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey


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


class UserStars(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'note')


class UserLikes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'note')


class Comment(MPTTModel):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    body = models.TextField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return f'By {self.user.username}'

    class MPTTMeta:
        order_insertion_by = ('-created',)

    class Meta:
        ordering = ['-created']


class CommentMetaData(models.Model):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='meta_data')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)


class UserCommentRating(models.Model):
    RATING_CHOICES = [
        ('LIKE', 'like'),
        ('DISLIKE', 'dislike'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    rating = models.CharField(max_length=7, choices=RATING_CHOICES)

    class Meta:
        unique_together = ('user', 'comment')
