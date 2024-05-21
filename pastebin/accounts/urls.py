from django.urls import path
from .views import UserCreateAPI, UserDeleteAPI, get_me


urlpatterns = [
    path('signup/', UserCreateAPI.as_view(), name='create_user'),
    path('delete/', UserDeleteAPI.as_view(), name='delete_user'),
    path('me/', get_me)
]
