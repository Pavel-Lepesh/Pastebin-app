from django.urls import path
from .views import UserStarsView

urlpatterns = [
    path('', UserStarsView.as_view({'get': 'retrieve'}), name='my_stars'),
    path('<str:hash_link>', UserStarsView.as_view({'post': 'create', 'delete': 'destroy'}), name='manage_stars'),
]
