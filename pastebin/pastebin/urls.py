from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from notes.views import URLNoteAPIView
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView,  # noqa
                                            TokenRefreshView, TokenVerifyView)

router = routers.SimpleRouter()
router.register(r'', URLNoteAPIView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('v1/accounts/', include('accounts.urls')),
    path('v1/comments/', include('comments.urls')),
    path('v1/mystars/', include('user_stars.urls')),
    path('v1/', include('notes.urls')),
    path('/schema/', SpectacularAPIView.as_view(), name='schema'),
    path("doc/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # for local tests
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]

admin.site.site_header = 'Pastebin administration'
