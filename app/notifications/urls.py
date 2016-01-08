from django.conf.urls import url
from .views import ShowView
from .api import NotificationApiView, NotificationsListApiView


urlpatterns = [
                url(r'api/notification/(?P<pk>\d+)$',
                    NotificationApiView.as_view(),
                    name='notification_api_dismiss'),
                url(r'api/notifications$',
                    NotificationsListApiView.as_view(),
                    name='notifications_api_list'),
                url(r'^(?P<pk>\d+)$',
                    ShowView.as_view(),
                    name='notification_show'),
]
