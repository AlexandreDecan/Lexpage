from django.conf.urls import patterns
from django.conf.urls import url

from views_search import SearchView

urlpatterns = patterns('', 
                url(r'^$',
                    SearchView.as_view(),
                    name='search'),
)

