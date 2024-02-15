from django.urls import path, re_path
from api.views import LinkAPIView, LikePost, UserStars
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView
from .views import NoteComments

urlpatterns = [
    re_path(
        r'^comments/(?P<hash_link>[\w-]+)/(?P<note_comment_id>\d+)/(?P<action_>(like|dislike))/(?P<cancel>cancel)?$',
        NoteComments.as_view({'post': 'rating'})),
    path('comments/<str:hash_link>', NoteComments.as_view({'get': 'list', 'post': 'create'}),
         name='get_and_post_comment'),
    path('comments/<str:hash_link>/<int:note_comment_id>', NoteComments.as_view({'patch': 'partial_update',
                                                                                 'delete': 'destroy'}),
         name='patch_and_delete_comment'),
    path('rating/<str:hash_link>', LikePost.as_view({'get': 'retrieve', 'post': 'like'}), name='like_or_get_note'),
    path('rating/<str:hash_link>/cancel', LikePost.as_view({'post': 'cancel_like'}), name='cancel_like_note'),
    path('mystars/', UserStars.as_view({'get': 'retrieve'}), name='my_stars'),
    path('mystars/delete/<str:hash_link>', UserStars.as_view({'delete': 'destroy'}), name='delete_star'),
    path('addstar/<str:hash_link>', UserStars.as_view({'post': 'create'}), name='add_star'),
    path('notes/', LinkAPIView.as_view({'get': 'list', 'post': 'create'}), name='get_create_note'),
    path('notes/usernotes/<int:user_id>', LinkAPIView.as_view({'get': 'public'}, name='get_public_note')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
