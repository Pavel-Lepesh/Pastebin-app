"""
URL configuration for pastebin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from api.views import LinkAPIView, URLNoteAPIView
from hash_generator.views import StartGenerate
from rest_framework import routers
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView


router = routers.SimpleRouter()
router.register(r'', URLNoteAPIView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('start-generate/', StartGenerate.as_view()),
    path('api/v1/notes/', LinkAPIView.as_view({'get': 'list', 'post': 'create'})),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")
]
