from django.urls import include, path
from django.contrib.flatpages.views import flatpage

from views import homepage

from django.contrib import admin


urlpatterns = [
    # Applications URLs
    path('accounts/', include('profile.auth_urls')),
    path('registration/', include('profile.register_urls')),
    path('profile/', include('profile.urls')),
    path('slogan/', include('slogan.urls')),
    path('minichat/', include('minichat.urls')),
    path('posts/', include('blog.urls')),
    path('messaging/', include('messaging.urls')),
    path('board/', include('board.urls')),
    path('notifications/', include('notifications.urls')),

    # Specific URLs
    path('', homepage, name='homepage'),
    path('search/', include('commons.urls_search')),
    path('markup/', include('commons.urls_markup')),
    path('about/', flatpage, {'url': '/about/'}, name='about'),

    # Django admin URLs
    path('admin/', admin.site.urls),

    # Flatpages URLs
    path('pages/', include('django.contrib.flatpages.urls')),
]

