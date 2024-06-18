from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from notes.models import Note


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


class CommentMetaData(models.Model):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='meta_data')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
