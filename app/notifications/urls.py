from django.urls import path
from .views import ShowView
from .api import NotificationApiView, NotificationsListApiView


urlpatterns = [
    path('api/notification/<int:pk>', NotificationApiView.as_view(), name='notification_api_dismiss'),
    path('api/notifications', NotificationsListApiView.as_view(), name='notifications_api_list'),
    path('<int:pk>', ShowView.as_view(), name='notification_show'),
]
