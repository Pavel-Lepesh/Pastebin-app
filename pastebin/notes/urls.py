from django.urls import path
from notes.views import LikePost, LinkAPIView, RecentPosts, PrivateLinkAPI


urlpatterns = [
    path('rating/<str:hash_link>', LikePost.as_view({'get': 'retrieve', 'post': 'like'}), name='like_or_get_note'),
    path('rating/<str:hash_link>/cancel', LikePost.as_view({'post': 'cancel_like'}), name='cancel_like_note'),
    path('notes/', LinkAPIView.as_view({'get': 'list', 'post': 'create'}), name='get_create_note'),
    path('notes/usernotes/<int:user_id>', LinkAPIView.as_view({'get': 'public'}, name='get_public_note')),
    path('recent/<int:limit>/', RecentPosts.as_view({'get': 'list'}), name='recent_posts'),
    path('own_private_link/<str:hash_link>', PrivateLinkAPI.as_view({'post': 'post'}), name='create_private_link'),
    path('private_link/<str:private_link>', PrivateLinkAPI.as_view({'get': 'get', 'delete': 'delete'}), name='get_delete_private_link'),
]
