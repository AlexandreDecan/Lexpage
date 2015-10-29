from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from django.core.urlresolvers import reverse_lazy

from django.views.generic import RedirectView
from .views import PostListView, PostShowView, PendingPostListView
from .views import DraftPostListView, PostCreateView, PostEditView, DraftPostEditView, PendingPostEditView
from .views import JSONTagListView, TagListView, PostCommentsView

from .feeds import LatestEntriesFeed

from datetime import date


post_patterns = patterns('',
                         url(r'^$',
                             PostShowView.as_view(),
                             name='blog_post_show'),
                         url(r'^edit/$',
                             PostEditView.as_view(),
                             name='blog_post_edit'),
                         url(r'^comments/$',
                             PostCommentsView.as_view(),
                             name='blog_post_comments'),
                         )

draft_patterns = patterns('',
                          url(r'^$',
                              DraftPostListView.as_view(),
                              name='blog_draft_list'),
                          url(r'^create/$',
                              PostCreateView.as_view(),
                              name='blog_draft_create'),
                          url(r'^(?P<pk>\d+)/$',
                              DraftPostEditView.as_view(),
                              name='blog_draft_edit'),
                          )

draft_patterns += patterns('django.contrib.flatpages.views',
                           url(r'^help/$', 'flatpage', {'url': '/bloghelp/'}, name='blog_draft_help'),
                           )

pending_patterns = patterns('',
                            url(r'^$',
                                PendingPostListView.as_view(),
                                name='blog_pending_list'),
                            url(r'^(?P<pk>\d+)/$',
                                PendingPostEditView.as_view(),
                                name='blog_pending_edit'),
                            )

tag_patterns = patterns('',
                        url(r'^list.json$',
                            JSONTagListView.as_view(),
                            name='blog_tags_json'),
                        url(r'^$',
                            TagListView.as_view(),
                            {'taglist': ''},
                            name='blog_tags'),
                        url(r'^(?P<taglist>[\w+\-]+)/$',
                            TagListView.as_view(),
                            name='blog_tags'),
                        url(r'^(?P<taglist>[\w+\-]+)/(?P<page>\d+)/$',
                            TagListView.as_view(),
                            name='blog_tags'),
                        )

urlpatterns = patterns('',
                       url(r'^archives/$',
                           RedirectView.as_view(
                               url=reverse_lazy('blog_archives',
                                                kwargs={'year': date.today().year, 'month': date.today().month})
                           ),
                           name='blog_archives'),
                       url(r'^archives/(?P<year>\d{4})/(?P<month>\d+)/$',
                           PostListView.as_view(month_format='%m'),
                           name='blog_archives'),

                       url(r'^(?P<pk>\d+)/',
                           include(post_patterns)),
                       url(r'^(?P<pk>\d+)-(?P<slug>[\w-]+)/',
                           include(post_patterns)),

                       url(r'^pending/',
                           include(pending_patterns)),
                       url(r'^draft/',
                           include(draft_patterns)),

                       url(r'^tags/',
                           include(tag_patterns)),

                       url(r'^rss/$',
                           LatestEntriesFeed(),
                           name='blog_rss'),
                       )

