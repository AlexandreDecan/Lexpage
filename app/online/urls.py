from django.conf.urls import url
from .views import online_ping

urlpatterns = [
    url(r'ping/$',
        online_ping,
        name='online_ping'),
]
