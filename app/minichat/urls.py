from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from .views import MessageListView
from .api import MinichatLatestMessagesView, MinichatMessagePostView
from datetime import date


urlpatterns = [
    path('archives/', RedirectView.as_view(
            url=reverse_lazy('minichat_archives',kwargs={'year': date.today().year, 'month': date.today().month}),
            permanent=False
        ), name='minichat_archives'),
    path('archives/<int:year>/<int:month>/', MessageListView.as_view(month_format='%m'), name='minichat_archives'),
    path('post/', MinichatMessagePostView.as_view(), name='minichat_post'),
    path('api/minichat-api-latest', MinichatLatestMessagesView.as_view(), name='minichat_latest_view'),
]
