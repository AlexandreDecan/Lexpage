from django.urls import path
from .views import SloganListView, SloganAddView

urlpatterns = [
   path('add/', SloganAddView.as_view(), name='slogan_add'),
   path('list/', SloganListView.as_view(), {'page': 'last'}, name='slogan_list'),
   path('list/<int:page>/', SloganListView.as_view(), name='slogan_list'),
]
