from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from django.core.urlresolvers import reverse_lazy

from views import DismissView, ShowView


urlpatterns = patterns('', 
                url(r'^(?P<pk>\d+)/dismiss/$', 
                    DismissView.as_view(), 
                    name='notification_dismiss'),
                url(r'^(?P<pk>\d+)/show/$', 
                    ShowView.as_view(),
                    name='notification_show'), 
)
