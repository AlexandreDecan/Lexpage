from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url 

from models import MessageBox

from views import MessageListView, ThreadListView, ReplyView, MarkThreadView, NewThreadView

thread_patterns = patterns('', 
       url(r'^$', 
           MessageListView.as_view(),
           name='messaging_show'),

       url(r'^reply/$',
           ReplyView.as_view(),
           name='messaging_reply'),

       url(r'^mark_archived/$', 
           MarkThreadView.as_view(), 
           {'mark': 'archived'},
           name='messaging_mark_archived'),
       url(r'^mark_unarchived/$',
           MarkThreadView.as_view(),
           {'mark': 'unarchived'},
           name='messaging_mark_unarchived'),
       url(r'^mark_deleted/$', 
           MarkThreadView.as_view(),
           {'mark': 'deleted'},
           name='messaging_mark_deleted'),
       url(r'^mark_starred/$', 
           MarkThreadView.as_view(), 
           {'mark': 'starred'},
           name='messaging_mark_starred'),
       url(r'^mark_unstarred/$',
           MarkThreadView.as_view(),
           {'mark': 'unstarred'},
           name='messaging_mark_unstarred'),
       url(r'^mark_read/$',
           MarkThreadView.as_view(),
           {'mark': 'read'},
           name='messaging_mark_read'),       
       url(r'^mark_unread/$',
           MarkThreadView.as_view(),
           {'mark': 'unread'},
           name='messaging_mark_unread'),
             
)

urlpatterns = patterns('', 
       url(r'^$', 
           ThreadListView.as_view(),
           name='messaging_inbox'),
       url(r'^messaging_archived/$', 
           ThreadListView.as_view(),
           {'filter': 'archived'},
           name='messaging_archived'),

       url(r'^create/$', 
           NewThreadView.as_view(),
           name='messaging_create'),

       url(r'^create/(?P<username>[\w.@+-_]+)/$', 
           NewThreadView.as_view(),
           name='messaging_create'),

       url(r'^(?P<thread>\d+)/',
           include(thread_patterns)),
)
