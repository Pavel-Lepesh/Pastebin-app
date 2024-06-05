from django.urls import path
from .views import UserCreateAPI, UserDeleteAPI, get_me, get_all_users, delete_user


urlpatterns = [
    path('signup/', UserCreateAPI.as_view(), name='create_user'),
    path('delete/', UserDeleteAPI.as_view(), name='delete_user'),
    path('me/', get_me),
    path("all_users/", get_all_users),
    path("del_user/<int:user_id>", delete_user)
]
