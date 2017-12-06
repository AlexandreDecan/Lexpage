from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from .views import MessageListView
from .api import MinichatLatestMessagesView, MinichatMessagePostView
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
    url(r'post/$',
        MinichatMessagePostView.as_view(),
        name='minichat_post'),
    url(r'api/minichat-api-latest$',
        MinichatLatestMessagesView.as_view(),
        name='minichat_latest_view'),
]
