from django.contrib import admin
from api.models import Note, Comment


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_update', 'availability')
    ordering = ['-time_update']
    list_editable = ('availability',)
    list_display_links = ('id', 'title')
    list_per_page = 10


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'updated')
    ordering = ['-updated']
    list_display_links = ('id',)
    list_per_page = 10
