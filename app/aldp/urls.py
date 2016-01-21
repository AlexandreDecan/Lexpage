from django.conf.urls import url
from .views import SeasonCreateView

urlpatterns = [
    url(r'^season/create/$',
        SeasonCreateView.as_view(),
        name='season_create'),
]

