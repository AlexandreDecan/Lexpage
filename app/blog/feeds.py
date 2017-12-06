from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy

from .models import BlogPost


class LatestEntriesFeed(Feed):
    title = 'Derniers billets'
    link = reverse_lazy('blog_archives')
    description = 'Derniers billets postés sur Lexpage'

    def items(self):
        return BlogPost.published.order_by('-date_published')[:10]

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.date_published

    def item_description(self, item):
        return item.abstract

    def item_link(self, item):
        return reverse_lazy('blog_post_show', kwargs={'pk': item.pk, 'slug': item.slug})
