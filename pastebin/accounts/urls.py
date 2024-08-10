from django.urls import path

from .views import UserCreateAPI, UserDeleteAPI, delete_user, get_all_users

urlpatterns = [
    path('signup/', UserCreateAPI.as_view(), name='create_user'),
    path('delete/', UserDeleteAPI.as_view(), name='delete_user'),
    path("all_users/", get_all_users),
    path("del_user/<int:user_id>", delete_user)
]
