#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.http import HttpResponse, Http404
from django.views.generic import ListView, View
#from django.views.generic.base import View
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
    queryset = Message.objects.order_by('-date')[:20]
    template_name = 'minichat/latests.html'
    context_object_name = 'message_list'


class MessagePostView(FormView):
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

    def notifications(self, user, message):
        """
        Parse the given message to find @name anchors. For every (unique) 
        anchor x, check if x is a username. If it is, send a notification 
        to this user. 
        """

        candidates = [x[0] for x in re.findall(r'@([\w\-_]+)(\b|\W)', message.text)]
        targets = set()
        
        for candidate in candidates:
            try: 
                s = ActiveUser.objects.all().get(username__iexact=candidate)
                targets.add(s)
            except ActiveUser.DoesNotExist:
                # print '%s not found' % candidate
                pass
        
        targets = list(targets)
        for target in targets:
            notify.minichat_warn(target, message)

        if len(targets) > 0 :
            if len(targets) == 1:
                messages.success(self.request, 'Une notification a été envoyée à %s suite à votre message sur le minichat.' % targets.pop().get_username())
            else:
                users_list = ', '.join([x.get_username() for x in targets[:-2]]) + ' et ' + targets[-1].get_username()
                messages.success(self.request, 'Une notification a été envoyée à %s suite à votre message sur le minichat.' % users_list)

        return targets



    def form_valid(self, form):
        response = super(MessagePostView, self).form_valid(form)
        user = self.request.user
        text = form.cleaned_data['text']
        message = Message(user=user, text=text)
        message.save()
        
        # Check for notifications
        try:
            self.notifications(self.request.user, message)
        except Exception as e: 
            print e, e.message


        if self.request.is_ajax():
            return self.render_to_json_response({'result': 'ok'})
        else:
            return response



# Not used at the moment, but functionnal. 
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
