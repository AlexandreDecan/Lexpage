#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy

from django.views.generic import ListView, View
from django.views.generic.edit import FormView

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages
from django.db.models import F

from profile.models import ActiveUser
from notifications import notify

from forms import NewThreadForm, ReplyForm
from models import Message, Thread, MessageBox

import copy


class ReplyView(FormView):
    template_name = None
    form_class = ReplyForm
    success_url = None

    dispatch = method_decorator(login_required)(FormView.dispatch)

    def form_valid(self, form):
        box = get_object_or_404(MessageBox.objects, thread=self.kwargs['thread'], user=self.request.user)
        box.thread.postMessage(self.request.user, form.cleaned_data['text'])
        notify.messaging_mesage_new(self.request.user, box.thread)
        messages.success(self.request, "Message enregistré.")
        return redirect(reverse_lazy('messaging_show', kwargs={'thread': self.kwargs['thread']}))

    def form_invalid(self, form):
        messages.error(self.request, '\n'.join(form.text.errors))
        return redirect(reverse_lazy('messaging_show', kwargs={'thread': self.kwargs['thread']}))


class MarkThreadView(View):
    dispatch = method_decorator(login_required)(View.dispatch)

    def get(self, request, *args, **kwargs):
        thread = kwargs['thread']
        if 'next' in self.request.GET:
            next = self.request.GET['next']
        else:
            next = None
        mark = kwargs['mark']

        if mark not in ['archived', 'unarchived', 'starred', 'unstarred', 'read', 'unread', 'deleted']:
            return redirect(reverse_lazy('messaging_show', kwargs={'thread': thread}))

        box = get_object_or_404(MessageBox.objects, thread=kwargs['thread'], user=self.request.user)

        if mark == 'archived':
            messages.success(request, 'La discussion a été déplacée vers les archives.')
            box.mark_archived()
        elif mark == 'unarchived':
            messages.success(request, 'La discussion a été déplacée vers la boîte de réception.')
            box.mark_normal()
        elif mark == 'starred':
            messages.success(request, 'Une étoile a été ajoutée à la discussion.')
            box.mark_starred()
        elif mark == 'unstarred':
            messages.success(request, 'Une étoile a été retirée de la discussion.')
            box.mark_unstarred()
        elif mark == 'read':
            messages.success(request, 'La discussion a été marquée comme lue.')
            box.mark_read()            
        elif mark == 'unread':
            messages.success(request, 'La discussion a été marquée comme non-lue.')
            box.mark_unread()
        elif mark == 'deleted':
            messages.success(request, 'La discussion a été supprimée.')
            box.mark_deleted()
            if next == 'thread':
                next = None

        if next == 'archived':
            return redirect(reverse_lazy('messaging_archived'))
        elif next == 'thread':
            return redirect(reverse_lazy('messaging_show', kwargs={'thread': kwargs['thread']}))
        else:
            return redirect(reverse_lazy('messaging_inbox'))



class NewThreadView(FormView):
    template_name = 'messaging/thread_new.html'
    form_class = NewThreadForm
    success_url = None  # Is set according to the new created thread

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if 'username' in kwargs:
            self.initial_target = kwargs['username']
        else:
            self.initial_target = None
        return FormView.dispatch(self, *args, **kwargs)

    def get_initial(self):
        initial = FormView.get_initial(self)
        if self.initial_target:
            user = get_object_or_404(ActiveUser, username=self.initial_target)
            initial['recipients'] = user
        return initial

    def get_form_kwargs(self):
        kwargs = FormView.get_form_kwargs(self)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        # Remove user from recipients, if needed
        for recipient in data['recipients']:
            if recipient.get_username() == self.request.user.get_username():
                data['recipients'].remove(recipient)
                break
        new_box = Thread.objects.createThread(self.request.user, data['title'], data['text'], data['recipients'])
        notify.messaging_thread_new(self.request.user, new_box.thread)
        messages.success(self.request, 'La nouvelle conversation a été enregistrée.')
        return redirect(reverse_lazy('messaging_show', kwargs={'thread': new_box.thread.pk}))



class MessageListView(ListView):
    template_name = 'messaging/thread_show.html'
    context_object_name = 'message_list'

    # See dispatch method below
    # dispatch = method_decorator(login_required)(ListView.dispatch)

    def get_queryset(self):
        return Message.objects.filter(thread=self.box.thread)

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context['user_list'] = self.box.thread.get_recipients()
        context['date_read'] = copy.copy(self.box.date_read)
        context['box'] = self.box
        context['form'] = ReplyForm()
        
        self.box.mark_read()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.box = get_object_or_404(MessageBox.objects, thread=self.kwargs['thread'], user=self.request.user)
        return ListView.dispatch(self, request, *args, **kwargs)



class ThreadListView(ListView):
    template_name = 'messaging/thread_list.html'
    context_object_name = 'box_list'

    dispatch = method_decorator(login_required)(ListView.dispatch)

    def get_queryset(self):
        if 'filter' in self.kwargs and self.kwargs['filter'] == 'archived':
            manager = MessageBox.archived
        else:
            manager = MessageBox.unarchived
        return manager.all().filter(user=self.request.user).order_by('-thread__last_message__date')

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)

        # Set '?next=' if needed
        if 'filter' in self.kwargs and self.kwargs['filter'] == 'archived':
            context['archived'] = True
            context['next'] = '?next=archived'

        return context
