from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from .views import MessageListView, LatestsView, MessagePostView, UsersListView
from datetime import date

urlpatterns = [
                       url(r'^archives/$',
                           RedirectView.as_view(
                               url=reverse_lazy('minichat_archives',
                                                kwargs={'year': date.today().year, 'month': date.today().month}),
                               permanent=False
                           ),
                           name='minichat_archives'),
                       url(r'^archives/(?P<year>\d{4})/(?P<month>\d+)/$',
                           MessageListView.as_view(month_format='%m'),
                           name='minichat_archives'),
                       url(r'latests/$',
                           LatestsView.as_view(),
                           name='minichat_latests'),
                       url(r'post/$',
                           MessagePostView.as_view(),
                           name='minichat_post'),
                       url(r'users.json$',
                           UsersListView.as_view(),
                           name='minichat_userslist'),
]
