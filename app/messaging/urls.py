from django.urls import include, path

from .views import MessageListView, ThreadListView, ReplyView, MarkThreadView, NewThreadView

thread_patterns = [
    path('', MessageListView.as_view(), name='messaging_show'),

    path('reply/', ReplyView.as_view(), name='messaging_reply'),

    path('mark_archived/', MarkThreadView.as_view(), {'mark': 'archived'}, name='messaging_mark_archived'),
    path('mark_unarchived/', MarkThreadView.as_view(), {'mark': 'unarchived'}, name='messaging_mark_unarchived'),
    path('mark_deleted/', MarkThreadView.as_view(), {'mark': 'deleted'}, name='messaging_mark_deleted'),
    path('mark_starred/', MarkThreadView.as_view(), {'mark': 'starred'}, name='messaging_mark_starred'),
    path('mark_unstarred/', MarkThreadView.as_view(), {'mark': 'unstarred'}, name='messaging_mark_unstarred'),
    path('mark_read/', MarkThreadView.as_view(), {'mark': 'read'}, name='messaging_mark_read'),
    path('mark_unread/', MarkThreadView.as_view(), {'mark': 'unread'}, name='messaging_mark_unread'),
]

urlpatterns = [
    path('', ThreadListView.as_view(), name='messaging_inbox'),
    path('messaging_archived/', ThreadListView.as_view(), {'filter': 'archived'}, name='messaging_archived'),

    path('create/', NewThreadView.as_view(), name='messaging_create'),

    path('create/<str:username>/', NewThreadView.as_view(), name='messaging_create'),

    path('<int:thread>/', include(thread_patterns)),
]
