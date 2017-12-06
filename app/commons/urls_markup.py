from django.urls import path, re_path
from django.contrib.flatpages.views import flatpage

from .views_markup import MarkupPreviewView

urlpatterns = [
    re_path('^(?P<markup>(bbcode)|(markdown))/preview/$', MarkupPreviewView.as_view(), name='markup_preview'),
    path('bbcode/', flatpage, {'url': '/bbcode/'}, name='markup_bbcode'),
    path('markdown/', flatpage, {'url': '/markdown/'}, name='markup_markdown'),
]
