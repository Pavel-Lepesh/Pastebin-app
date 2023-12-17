from django.urls import path
from api.views import LinkAPIView, LikePost, UserStars
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView


urlpatterns = [
    path('rating/<str:hash_link>', LikePost.as_view()),
    path('mystars/', UserStars.as_view({'get': 'retrieve'})),
    path('mystars/delete/<str:hash_link>', UserStars.as_view({'delete': 'destroy'})),
    path('addstar/<str:hash_link>', UserStars.as_view({'post': 'create'})),
    path('notes/', LinkAPIView.as_view({'get': 'list', 'post': 'create'})),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")
]