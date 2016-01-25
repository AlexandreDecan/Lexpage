from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import linebreaksbr

from commons.templatetags.markup_bbcode import stripbbcode
from .models import Thread, Message

import datetime


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
        message = linebreaksbr(stripbbcode(item.text))
        return 'Message par %s:<br/><br/>%s' % (item.author.username, message)

    def item_link(self, item):
        return item.get_absolute_url()

