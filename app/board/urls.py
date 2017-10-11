from django.conf.urls import include
from django.conf.urls import url
from .views import ThreadView, ThreadUnreadRedirectView, ThreadReplyView, \
                ThreadMarkUnreadView, ThreadDeleteView, ThreadCreateView, \
                MessageRedirectView, MessageEditView, \
                MessageDeleteView, MessageMarkUnreadView, \
                BoardLatestsView, BoardArchivesView, BoardArchivesMessagesView, \
                ThreadCreateForPostView, FollowedView

from .feeds import LatestsFeed
from .api import MessageViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'message', MessageViewSet, 'board_api_message')


thread_patterns = [
                url(r'^$',
                    ThreadView.as_view(),
                    {'page': 1},
                    name='board_thread_show'),
                url(r'^(?P<page>\d+)/$',
                    ThreadView.as_view(),
                    name='board_thread_show'),
                url(r'^last/(#last)?$',
                    ThreadView.as_view(),
                    {'page':'last'},
                    name='board_thread_show_last'),
                url(r'^unread/$',
                    ThreadUnreadRedirectView.as_view(),
                    name='board_thread_show_unread'),
                url(r'^reply/$',
                    ThreadReplyView.as_view(),
                    name='board_thread_reply'),
                url(r'^mark_unread/$',
                    ThreadMarkUnreadView.as_view(),
                    name='board_thread_mark_unread'),
                url(r'^delete/$',
                    ThreadDeleteView.as_view(),
                    name='board_thread_delete'),
]

message_patterns = [
                url(r'^$',
                    MessageRedirectView.as_view(),
                    name='board_message_show'),
                url(r'^edit/$',
                    MessageEditView.as_view(),
                    name='board_message_edit'),
                url(r'^moderate/$',
                    MessageEditView.as_view(),
                    name='board_message_moderate'),
                url(r'^mark_unread/$',
                    MessageMarkUnreadView.as_view(),
                    name='board_message_mark_unread'),
                url(r'^delete/$',
                    MessageDeleteView.as_view(),
                    name='board_message_delete'),
]

followed_patterns = [
                url(r'^$',
                    FollowedView.as_view(),
                    {'page': 'last', 'filter_unread': False},
                    name='board_followed'),
                url(r'^(?P<page>\d+)/$',
                    FollowedView.as_view(),
                    {'filter_unread': False},
                    name='board_followed'),
                url(r'^unread/$',
                    FollowedView.as_view(),
                    {'page': 'last', 'filter_unread': True},
                    name='board_followed_unread'),
                url(r'^unread/(?P<page>\d+)/$',
                    FollowedView.as_view(),
                    {'filter_unread': True},
                    name='board_followed_unread'),
]

urlpatterns = [
                url(r'^$',
                    BoardLatestsView.as_view(),
                    {'page': 1},
                    name='board_latests'),
                url(r'^(?P<page>\d+)/$',
                    BoardLatestsView.as_view(),
                    name='board_latests'),
                url(r'^archives/$',
                    BoardArchivesView.as_view(),
                    {'page': 'last'},
                    name='board_archives'),
                url(r'^archives/(?P<page>\d+)/$',
                    BoardArchivesView.as_view(),
                    name='board_archives'),
                url(r'^archives/messages/$',
                    BoardArchivesMessagesView.as_view(),
                    {'page': 'last'},
                    name='board_archives_messages'),
                url(r'^archives/messages/(?P<page>\d+)/$',
                    BoardArchivesMessagesView.as_view(),
                    name='board_archives_messages'),

                url(r'^followed/',
                    include(followed_patterns)),

                url(r'^create/$',
                    ThreadCreateView.as_view(),
                    name='board_create'),
                url(r'^comment/(?P<post>\d+)/$',
                    ThreadCreateForPostView.as_view(),
                    name='board_create_for_post'),

                url(r'^thread/(?P<thread>\d+)/',
                    include(thread_patterns)),
                url(r'^thread/(?P<thread>\d+)-(?P<slug>[\w-]+)/',
                    include(thread_patterns)),

                url(r'^message/(?P<message>\d+)/',
                    include(message_patterns)),

                url(r'^api/',
                    include(router.urls)),

                url(r'^rss/$',
                    LatestsFeed(),
                    name='board_rss'),
]


