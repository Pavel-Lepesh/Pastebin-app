from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Note, NoteMetaData


@receiver(post_save, sender=Note)
def create_note_metadata(sender, instance, created, **kwargs):
    if created:
        NoteMetaData.objects.create(note=instance)
