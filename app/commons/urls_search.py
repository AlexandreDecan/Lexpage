from django.conf.urls import url

from .views_search import SearchView

urlpatterns = [
                url(r'^$',
                    SearchView.as_view(),
                    name='search'),
]

