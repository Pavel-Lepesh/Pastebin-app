from django.contrib import admin
from django.urls import path, include
from notes.views import URLNoteAPIView
from rest_framework import routers
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView


router = routers.SimpleRouter()
router.register(r'', URLNoteAPIView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('accounts/', include('accounts.urls')),
    path('comments/', include('comments.urls')),
    path('mystars/', include('user_stars.urls')),
    path('notes/v1/', include('notes.urls')),
    path('/schema/', SpectacularAPIView.as_view(), name='schema'),
    path("doc/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")
]

admin.site.site_header = 'Pastebin administration'
