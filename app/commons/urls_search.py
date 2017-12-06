from django.urls import path

from .views_search import SearchView

urlpatterns = [
    path('', SearchView.as_view(), name='search'),
]

