from django.urls import path
from .views import UserCreateAPI


urlpatterns = [
    path('signup/', UserCreateAPI.as_view()),
]
