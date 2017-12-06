from django.urls import include, path, re_path

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
    path('', ThreadView.as_view(), {'page': 1}, name='board_thread_show'),
    path('<int:page>', ThreadView.as_view(), name='board_thread_show'),
    re_path(r'^last/(#last)?$', ThreadView.as_view(), {'page': 'last'}, name='board_thread_show_last'),
    path('unread/', ThreadUnreadRedirectView.as_view(), name='board_thread_show_unread'),
    path('reply/', ThreadReplyView.as_view(), name='board_thread_reply'),
    path('mark_unread/', ThreadMarkUnreadView.as_view(), name='board_thread_mark_unread'),
    path('delete/', ThreadDeleteView.as_view(), name='board_thread_delete'),
]

message_patterns = [
    path('', MessageRedirectView.as_view(), name='board_message_show'),
    path('edit/', MessageEditView.as_view(), name='board_message_edit'),
    path('moderate/', MessageEditView.as_view(), name='board_message_moderate'),
    path('mark_unread/', MessageMarkUnreadView.as_view(), name='board_message_mark_unread'),
    path('delete/', MessageDeleteView.as_view(), name='board_message_delete'),
]

followed_patterns = [
    path('', FollowedView.as_view(), {'page': 'last', 'filter_unread': False}, name='board_followed'),
    path('<int:page>/', FollowedView.as_view(), {'filter_unread': False}, name='board_followed'),
    path('unread/', FollowedView.as_view(), {'page': 'last', 'filter_unread': True}, name='board_followed_unread'),
    path('unread/<int:page>/', FollowedView.as_view(), {'filter_unread': True}, name='board_followed_unread'),
]

urlpatterns = [
    path('', BoardLatestsView.as_view(), {'page': 1}, name='board_latests'),
    path('<int:page>/', BoardLatestsView.as_view(), name='board_latests'),
    path('archives/', BoardArchivesView.as_view(), {'page': 'last'}, name='board_archives'),
    path('archives/<int:page>/', BoardArchivesView.as_view(), name='board_archives'),
    path('archives/messages/', BoardArchivesMessagesView.as_view(), {'page': 'last'}, name='board_archives_messages'),
    path('archives/messages/<int:page>/', BoardArchivesMessagesView.as_view(), name='board_archives_messages'),

    path('followed/', include(followed_patterns)),

    path('create/', ThreadCreateView.as_view(), name='board_create'),
    path('comment/<int:post>/', ThreadCreateForPostView.as_view(), name='board_create_for_post'),

    path('thread/<int:thread>/', include(thread_patterns)),
    path('thread/<int:thread>-<slug:slug>/', include(thread_patterns)),

    path('message/<int:message>/', include(message_patterns)),

    path('api/', include(router.urls)),

    path('rss/', LatestsFeed(), name='board_rss'),
]


