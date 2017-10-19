from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy

from .models import Message


class LatestsFeed(Feed):
    title = 'Discussions récentes'
    link = reverse_lazy('board_latests')
    description = 'Derniers messages dans les discussions'

    def items(self):
        return Message.objects.all().order_by('-date')[:30]

    def item_title(self, item):
        return item.thread.title

    def item_pubdate(self, item):
        return item.date

    def item_description(self, item):
        return 'Message par {}:\n\n{}'.format(item.author.username, item.text)

    def item_link(self, item):
        return item.get_absolute_url()

