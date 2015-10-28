#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.http import HttpResponse, Http404
from django.views.generic import ListView, View
from django.views.generic.edit import FormView
from django.views.generic.dates import MonthArchiveView

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages

from models import Message
from forms import MessageForm

from notifications import notify
from profile.models import ActiveUser

from datetime import date
# from calendar import timegm

import json
import re


class MessageListView(MonthArchiveView):
    """
    Display all the messages by month.
    """
    queryset = Message.objects.all()
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


class LatestsView(ListView):
    """
    Display the 20 latest messages.
    """
    queryset = Message.objects.order_by('-date')[:20]
    template_name = 'minichat/latests.html'
    context_object_name = 'message_list'


class MessagePostView(FormView):
    """
    Handle message submission.
    """
    form_class = MessageForm
    template_name = 'minichat/post.html'
    success_url = reverse_lazy('minichat_post')

    dispatch = method_decorator(login_required)(FormView.dispatch)

    def render_to_json_response(self, context, **kwargs):
        data = json.dumps(context)
        kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **kwargs)

    def form_invalid(self, form):
        response = super(MessagePostView, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        message = Message(user=self.request.user, text=form.cleaned_data['text'])
        message.save()

        # Notify users that are anchored in this message
        anchors = message.parse_anchors()
        for anchor in anchors:
            notify.minichat_warn(anchor, message)

        # Warn the user that we notified the other users
        if len(anchors) > 0:
            if len(anchors) > 1:
                anchors_text = ', '.join([x.get_username() for x in anchors[:-2]]) + ' et ' + anchors[-1].get_username()
            else:
                anchors_text = anchors[0].get_username()
            messages.success(self.request, 'Une notification a été envoyée à %s suite à votre message sur le minichat.' % anchors_text)

        if self.request.is_ajax():
            return self.render_to_json_response({'result': 'ok'})
        else:
            return super(MessagePostView, self).form_valid(form)


# Not used at the moment, but functional.
"""
class LatestsJSONView(View):
    def get(self, request):
        messages = Message.objects.order_by('-date')[:20]
        output = []
        for message in messages:
            output.append({
                'username': message.user.get_username(), 
                'avatar': message.user.profile.avatar,
                'text': message.text, 
                'timestamp': timegm(message.date.utctimetuple())
            })

        return HttpResponse(simplejson.dumps(output), content_type='application/json')
"""


class UsersListView(View):
    """
    Return a list of available users whose username starts with the value in `query`.
    """
    def get(self, request):
        query = request.GET.get('query', None)
        if not query or len(query) < 3:
            raise Http404

        users = ActiveUser.objects.filter(username__istartswith=query[1:])
        output = {'query': query, 'suggestions': []}
        for user in users:
            suggestion = {'value': '@%s' % user.get_username()}
            output['suggestions'].append(suggestion)

        return HttpResponse(json.dumps(output), content_type='application/json')
