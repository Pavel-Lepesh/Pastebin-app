from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'updated')
    ordering = ['-updated']
    list_display_links = ('id',)
    list_per_page = 10
