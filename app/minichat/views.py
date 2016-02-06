from django.views.generic import ListView
from django.views.generic.dates import MonthArchiveView

from .models import Message

from datetime import date


class MessageListView(MonthArchiveView):
    """
    Display all the messages by month.
    """
    queryset = Message.objects.all().reverse()
    date_field = 'date'
    make_object_list = True
    allow_future = False # Not really useful...
    allow_empty = True
    template_name = 'minichat/list.html'
    context_object_name = 'message_list'

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        context['date_list'] = Message.objects.dates('date', 'month')
        context['date_current'] = date(int(self.get_year()), int(self.get_month()), 1)
        return context

