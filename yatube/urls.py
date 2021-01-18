from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa


urlpatterns = [
    #  регистрация и авторизация
    path('auth/', include('users.urls')),
    #  если нужного шаблона для /auth не нашлось в файле users.urls —
    #  ищем совпадения в файле django.contrib.auth.urls
    path('auth/', include('django.contrib.auth.urls')),
    # импорт правил из приложения posts
    path('', include('posts.urls')),
    # приложение about
    path('about/', include('about.urls', namespace='about')),
    # импорт правил из приложения admin
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
