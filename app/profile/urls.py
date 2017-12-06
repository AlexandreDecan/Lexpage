from django.urls import path

from .views import ProfileChangeView, ProfileShowView, ProfileListView
from .api import UsernamesListView

urlpatterns = [
   path('edit/', ProfileChangeView.as_view(), name='profile_edit'),
   path('list/', ProfileListView.as_view(), {'page': 'last'}, name='profile_list'),
   path('list/<int:page>/', ProfileListView.as_view(), name='profile_list'),
   path('view/<str:username>/', ProfileShowView.as_view(), name='profile_show'),
   path('api/users', UsernamesListView.as_view(), name='profile_api_list'),
]

