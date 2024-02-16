from django.urls import path
from .views import UserCreateAPI, UserDeleteAPI


urlpatterns = [
    path('signup/', UserCreateAPI.as_view(), name='create_user'),
    path('delete/', UserDeleteAPI.as_view(), name='delete_user'),
]
