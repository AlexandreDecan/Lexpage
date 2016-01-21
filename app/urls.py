#!/usr/bin/python

from django.conf.urls import include, url
from django.contrib.flatpages.views import flatpage

from views import homepage

from django.contrib import admin


urlpatterns = [
    # Applications URLs
    url(r'^accounts/', include('profile.auth_urls')),
    url(r'^registration/', include('profile.register_urls')),
    url(r'^profile/', include('profile.urls')),
    url(r'^slogan/', include('slogan.urls')),
    url(r'^minichat/', include('minichat.urls')),
    url(r'^posts/', include('blog.urls')),
    url(r'^messaging/', include('messaging.urls')),
    url(r'^board/', include('board.urls')),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^aldp/', include('aldp.urls')),

    # Specific URLs
    url(r'^$', homepage, name='homepage'),
    url(r'^go.php$', homepage),
    url(r'^search/', include('commons.urls_search')),
    url(r'^markup/', include('commons.urls_markup')),
    url(r'^about/$', flatpage, {'url': '/about/'}, name='about'),

    # Django admin URLs
    url(r'^admin/', include(admin.site.urls)),

    # Flatpages URLs
    url(r'^pages/', include('django.contrib.flatpages.urls')),
]

