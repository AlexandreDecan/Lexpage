from django.conf.urls import url
from django.contrib.flatpages.views import flatpage

from .views_markup import MarkupPreviewView

urlpatterns = [
                url(r'^(?P<markup>(bbcode)|(markdown))/preview/$',
                    MarkupPreviewView.as_view(),
                    name='markup_preview'),
                url(r'^bbcode/$', flatpage, {'url': '/bbcode/'}, name='markup_bbcode'),
                url(r'^markdown/$', flatpage, {'url': '/markdown/'}, name='markup_markdown'),
]
