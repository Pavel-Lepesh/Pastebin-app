from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, CommentMetaData, Note, NoteMetaData


@receiver(post_save, sender=Comment)
def create_comment_metadata(sender, instance, created, **kwargs):
    if created:
        CommentMetaData.objects.create(comment=instance)


@receiver(post_save, sender=Note)
def create_note_metadata(sender, instance, created, **kwargs):
    if created:
        NoteMetaData.objects.create(note=instance)
