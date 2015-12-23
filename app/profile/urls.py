from django.conf.urls import url

from .views import ProfileChangeView, ProfileShowView, ProfileListView

urlpatterns = [
                       url(r'^edit/$',
                           ProfileChangeView.as_view(),
                           name='profile_edit'),
                       url(r'^list/$',
                           ProfileListView.as_view(),
                           {'page': 'last'},
                           name='profile_list'),
                       url(r'^list/(?P<page>\d+)/$',
                           ProfileListView.as_view(),
                           name='profile_list'),
                       url(r'^(?P<username>[\w\.@+\-_]+)/$',
                           ProfileShowView.as_view(),
                           name='profile_show'),
]

