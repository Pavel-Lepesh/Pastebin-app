from django.contrib import admin
from notes.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_update', 'availability')
    ordering = ['-time_update']
    list_editable = ('availability',)
    list_display_links = ('id', 'title')
    list_per_page = 10
