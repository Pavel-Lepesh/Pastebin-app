from django.urls import path, re_path
from api.views import LinkAPIView, LikePost, UserStars
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView
from .views import NoteComments


urlpatterns = [
    re_path(r'^comments/(?P<hash_link>[\w-]+)/(?P<note_comment_id>\d+)/(?P<action_>(like|dislike))/(?P<cancel>cancel)?$',
            NoteComments.as_view({'post': 'rating'})),
    path('comments/<str:hash_link>', NoteComments.as_view({'get': 'list', 'post': 'create'})),
    path('comments/<str:hash_link>/<int:note_comment_id>', NoteComments.as_view({'patch': 'partial_update',
                                                                                 'delete': 'destroy'})),
    path('rating/<str:hash_link>', LikePost.as_view({'get': 'retrieve', 'post': 'like'})),
    path('rating/<str:hash_link>/cancel', LikePost.as_view({'post': 'cancel_like'})),
    path('mystars/', UserStars.as_view({'get': 'retrieve'})),
    path('mystars/delete/<str:hash_link>', UserStars.as_view({'delete': 'destroy'})),
    path('addstar/<str:hash_link>', UserStars.as_view({'post': 'create'})),
    path('notes/', LinkAPIView.as_view({'get': 'list', 'post': 'create'})),
    path('notes/usernotes/<int:user_id>', LinkAPIView.as_view({'get': 'public_notes'})),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
