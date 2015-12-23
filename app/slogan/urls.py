from django.conf.urls import url

from .views import SloganListView, SloganAddView

urlpatterns = [
                       url(r'^add/$',
                           SloganAddView.as_view(),
                           name='slogan_add'),
                       url(r'^list/$',
                           SloganListView.as_view(), {'page':'last'},
                           name='slogan_list'),
                       url(r'^list/(?P<page>\d+)/$',
                           SloganListView.as_view(),
                           name='slogan_list'),
]
