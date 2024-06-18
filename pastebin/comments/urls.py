from django.urls import path, re_path

from .views import NoteComments

urlpatterns = [
    re_path(
        r'^(?P<hash_link>[\w-]+)/(?P<note_comment_id>\d+)/(?P<action_>(like|dislike))/(?P<cancel>cancel)?$',
        NoteComments.as_view({'post': 'rating'})),
    path('<str:hash_link>', NoteComments.as_view({'get': 'list', 'post': 'create'}), name='get_and_post_comment'),
    path('<str:hash_link>/<int:note_comment_id>', NoteComments.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
         name='patch_and_delete_comment'),
]
