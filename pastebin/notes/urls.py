from django.urls import path
from notes.views import LikePost, LinkAPIView, RecentPosts


urlpatterns = [
    path('rating/<str:hash_link>', LikePost.as_view({'get': 'retrieve', 'post': 'like'}), name='like_or_get_note'),
    path('rating/<str:hash_link>/cancel', LikePost.as_view({'post': 'cancel_like'}), name='cancel_like_note'),
    path('notes/', LinkAPIView.as_view({'get': 'list', 'post': 'create'}), name='get_create_note'),
    path('notes/usernotes/<int:user_id>', LinkAPIView.as_view({'get': 'public'}, name='get_public_note')),
    path('recent/<int:limit>/', RecentPosts.as_view({'get': 'list'}), name='recent_posts'),
]
