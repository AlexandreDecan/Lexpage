from django.urls import include, path, re_path, reverse_lazy

from django.views.generic import RedirectView
from django.contrib.flatpages.views import flatpage
from .views import PostListView, PostShowView, PendingPostListView, QuickShareCreateView
from .views import DraftPostListView, PostCreateView, PostEditView, DraftPostEditView, PendingPostEditView
from .views import TagListView, PostCommentsView
from .api import TagsListView
from .feeds import LatestEntriesFeed

from datetime import date

post_patterns = [
    path('', PostShowView.as_view(), name='blog_post_show'),
    path(r'edit/', PostEditView.as_view(), name='blog_post_edit'),
    path('comments/', PostCommentsView.as_view(), name='blog_post_comments'),
]

draft_patterns = [
    path('', DraftPostListView.as_view(),name='blog_draft_list'),
    path('create/', PostCreateView.as_view(), name='blog_draft_create'),
    path('<int:pk>/', DraftPostEditView.as_view(), name='blog_draft_edit'),
    path('help/', flatpage, {'url': '/bloghelp/'}, name='blog_draft_help'),
]

pending_patterns = [
    path('', PendingPostListView.as_view(), name='blog_pending_list'),
    path('<int:pk>', PendingPostEditView.as_view(), name='blog_pending_edit'),
]

tag_patterns = [
    path('api/list', TagsListView.as_view(), name='blog_api_tags'),
    path('', TagListView.as_view(), {'taglist': ''}, name='blog_tags'),
    re_path(r'^(?P<taglist>[\w+\-]+)/$', TagListView.as_view(), name='blog_tags'),
    re_path(r'^(?P<taglist>[\w+\-]+)/(?P<page>\d+)/$', TagListView.as_view(), name='blog_tags'),
]

urlpatterns = [
    path('archives/', RedirectView.as_view(
            url=reverse_lazy('blog_archives', kwargs={'year': date.today().year, 'month': date.today().month}),
            permanent=False,
        ), name='blog_archives'),
    path('archives/<int:year>/<int:month>/', PostListView.as_view(month_format='%m'), name='blog_archives'),

    path('<int:pk>/', include(post_patterns)),
    path('<int:pk>-<slug:slug>/', include(post_patterns)),

    path('quickshare/', QuickShareCreateView.as_view(), name='blog_quickshare_create'),

    path('pending/', include(pending_patterns)),
    path('draft/', include(draft_patterns)),
    path('tags/', include(tag_patterns)),

    path('rss/', LatestEntriesFeed(), name='blog_rss'),
]
