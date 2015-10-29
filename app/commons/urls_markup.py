from django.conf.urls import patterns
from django.conf.urls import url

from .views_markup import MarkupPreviewView

urlpatterns = patterns('', 
                url(r'^(?P<markup>(bbcode)|(markdown))/preview/$',
                    MarkupPreviewView.as_view(),
                    name='markup_preview'),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^bbcode/$', 'flatpage', {'url': '/bbcode/'}, name='markup_bbcode'),
    url(r'^markdown/$', 'flatpage', {'url': '/markdown/'}, name='markup_markdown'),
)
