#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy, reverse

from django.http import HttpResponse, Http404

from django.views.generic import View, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.db.models import F, Q
from django.contrib import messages

from models import Message, Thread, Flag, MessageHistory, BlogBoardLink

from blog.models import BlogPost
from notifications import notify 

from forms import MessageForm, MessageModerateForm, ThreadForm

import datetime
import json


MESSAGES_PER_THREAD = 10
LATESTS_IN_DAYS = 6
THREADS_PER_PAGE = 20
MESSAGES_PER_PAGE = 50  # archives


# Provide form
class ThreadView(ListView):
    template_name = 'board/thread_show.html'
    context_object_name = 'message_list'
    allow_empty = False
    queryset = None
    paginate_by = MESSAGES_PER_THREAD

    def get_queryset(self):
        self.thread = get_object_or_404(Thread.objects, pk=self.kwargs['thread'])
        return Message.objects.all().filter(thread=self.thread)

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        # Context also contains is_paginated, paginator, page_obj

        self.thread.annotate_flag(self.request.user)
        context['thread'] = self.thread

        # Do we need to display the last message of the previous page?
        if context['page_obj'].has_previous:
            previous_message = context['message_list'][0].previous()
            context['previous'] = previous_message

        # Update flag if needed
        last_index = len(context['message_list']) - 1
        Flag.objects.read(self.request.user, context['message_list'][last_index])

        # Display form if needed
        if self.request.user.is_authenticated():
            context['form'] = MessageForm()

        return context




class ThreadUnreadRedirectView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(RedirectView.dispatch)

    def get_redirect_url(self, **kwargs):
        # Last read message
        message = get_object_or_404(Flag.objects, thread=kwargs['thread'], user=self.request.user).message
        position = message.position()

        # If the last read is the last message (ie. "doubleclick" on flag)
        if message == message.thread.last_message:
            pass
        else:
            # First new message is at position + 1
            position = position + 1
        
        page = (position / MESSAGES_PER_THREAD) + 1
        anchor = '#new'
        
        return reverse('board_thread_show', 
                kwargs={'thread': kwargs['thread'], 'slug': message.thread.slug, 'page': page}) + anchor


class ThreadReplyView(FormView):
    template_name = 'board/thread_reply.html'
    form_class = MessageForm
    success_url = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.thread = get_object_or_404(Thread.objects, pk=self.kwargs['thread'])
        return FormView.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)
        context['thread'] = self.thread
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        self.thread.postMessage(self.request.user, data['text'])
        return FormView.form_valid(self, form)

    def get_success_url(self):
        return reverse_lazy('board_thread_show_last', 
                    kwargs={'thread': self.thread.pk, 'slug': self.thread.slug}) + '#last'




class ThreadMarkUnreadView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(RedirectView.dispatch)

    def get_redirect_url(self, **kwargs):
        thread = get_object_or_404(Thread.objects, pk=kwargs['thread'])
        # Remove flag if any
        try:
            flag = Flag.objects.all().get(thread=thread.pk, user=self.request.user)
            flag.delete()
        except Flag.DoesNotExist:
            pass
        messages.success(self.request, "La discussion a été marquée comme non-lue.")
        return reverse_lazy('board_latests')



class ThreadDeleteView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(RedirectView.dispatch)

    def get_redirect_url(self, **kwargs):
        thread = get_object_or_404(Thread.objects, pk=kwargs['thread'])
        if self.request.user.has_perm('board.can_destroy'):
            thread.delete()
            messages.success(self.request, "La discussion a été supprimée.")
            return reverse_lazy('board_latests')
        else:
            raise Http404



class ThreadCreateView(FormView):
    template_name = 'board/thread_create.html'
    form_class = ThreadForm
    success_url = None

    dispatch = method_decorator(login_required)(FormView.dispatch)

    def form_valid(self, form):
        data = form.cleaned_data
        thread = Thread(title=data['title'])
        thread.save()
        
        self.thread = thread    # For success url

        message = thread.postMessage(self.request.user, data['text'])
        return FormView.form_valid(self, form)

    def get_success_url(self):
        return reverse_lazy('board_thread_show_last', kwargs={'thread': self.thread.pk, 'slug': self.thread.slug})


class ThreadCreateForPostView(FormView):
    template_name = 'board/thread_create_for_post.html'
    form_class = ThreadForm
    success_url = None

    dispatch = method_decorator(login_required)(FormView.dispatch)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.blogpost = get_object_or_404(BlogPost.published, pk=kwargs['post'])
        return FormView.dispatch(self, request, *args, **kwargs)
 
    def get_initial(self):
        initial = {}
        initial['title'] = 'Billet - %s' % (self.blogpost.title)
        return initial

    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)
        context['post'] = self.blogpost
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        thread = Thread(title=data['title'])
        thread.save()
        
        link = BlogBoardLink(thread=thread, post=self.blogpost)
        link.save()

        self.thread = thread    # For success url

        message = thread.postMessage(self.request.user, data['text'])
        return FormView.form_valid(self, form)

    def get_success_url(self):
        return reverse_lazy('board_thread_show_last', kwargs={'thread': self.thread.pk, 'slug': self.thread.slug})



class MessageRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        message = get_object_or_404(Message.objects, pk=kwargs['message'])
        position = message.position()
        page = (position / MESSAGES_PER_THREAD) + 1
        return reverse('board_thread_show', 
               kwargs={'thread': message.thread.pk, 
                        'slug': message.thread.slug, 
                        'page': page}) + "#msg" + str(message.pk)





class MessageEditView(FormView):
    template_name = 'board/message_edit.html'
    form_class = MessageForm
    success_url = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.message = get_object_or_404(Message.objects, pk=self.kwargs['message'])
        
        can_we = (((self.message.author == self.request.user) and not self.message.moderated)
                    or (self.request.user.has_perm('board.can_moderate')))
        if not can_we:
            raise Http404
        return FormView.dispatch(self, request, *args, **kwargs)

    def get_form(self, form_class):
        if self.request.user.has_perm('board.can_moderate'):
            form_class = MessageModerateForm
        else:
            form_class = MessageForm
        return FormView.get_form(self, form_class)

    def get_initial(self):
        initial = {}
        initial['text'] = self.message.text
        initial['moderated'] = self.message.moderated
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        self.message.modify(self.request.user, data['text'])
        if self.request.user.has_perm('board.can_moderate') and ('moderated' in data):
            if data['moderated']:
                self.message.moderated = True
                notify.board_post_moderate(self.request.user, self.message)
                messages.warning(self.request, "Le message a été modéré.")
            else:
                self.message.moderated = False
            self.message.save()
        messages.success(self.request, "Le message a été modifié.")
        return FormView.form_valid(self, form)

    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)
        context['message'] = self.message

        # Message history
        context['history_list'] = MessageHistory.objects.all().filter(message=self.message).order_by('-date')
        return context

    def get_success_url(self):
        return reverse_lazy('board_message_show', kwargs={'message': self.message.pk})



class MessageDeleteView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(RedirectView.dispatch)

    def get_redirect_url(self, **kwargs):
        message = get_object_or_404(Message.objects, pk=kwargs['message'])
        if self.request.user.has_perm('board.can_destroy'):
            anchor = message.delete()
            messages.success(self.request, "Le message a été supprimé.")
            if anchor:
                return reverse_lazy('board_message_show', kwargs={'message': anchor.pk})
            else:
                messages.success(self.request, 'La discussion étant vide, elle a été supprimée également.')
                return reverse_lazy('board_latests')
        else:
            raise Http404



class MessageMarkUnreadView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(RedirectView.dispatch)

    def get_redirect_url(self, **kwargs):
        message = get_object_or_404(Message.objects, pk=kwargs['message'])
        Flag.objects.unread(self.request.user, message)
        messages.success(self.request, "Le nouveau marqueur de lecture a été enregistré.")
        return reverse_lazy('board_latests')
        


class MessageJSONView(View):
    def get(self, request, **kwargs):
        message = get_object_or_404(Message.objects, pk=kwargs['message'])
        output = {'text': message.text, 
                'author': message.author.username,
                'date' : str(message.date)}
        return HttpResponse(json.dumps(output), mimetype='application/json')



class BoardLatestsView(ListView):
    template_name = 'board/latests.html'
    context_object_name = 'thread_list'
    queryset = None

    def get_queryset(self):
        date_limit = datetime.date.today() - datetime.timedelta(LATESTS_IN_DAYS)
        date_limit = datetime.datetime(date_limit.year, date_limit.month, date_limit.day)
        threads = Thread.objects.all().filter(last_message__date__gte=date_limit).order_by('-date_created')
        for thread in threads:
            thread.annotate_flag(self.request.user)
        return threads


class BoardArchivesView(ListView):
    template_name = 'board/archives.html'
    context_object_name = 'thread_list'
    allow_empty = True
    queryset = Thread.objects.all()
    paginate_by = THREADS_PER_PAGE
    paginate_orphans = THREADS_PER_PAGE / 5

    def paginate_queryset(self, queryset, page_size):
        (paginator, page, object_list, is_paginated) = ListView.paginate_queryset(self, queryset, page_size)
        for thread in object_list:
            thread.annotate_flag(self.request.user)
        return (paginator, page, object_list, is_paginated)


class BoardArchivesMessagesView(ListView):
    template_name = 'board/archives_messages.html'
    context_object_name = 'message_list'
    allow_empty = True
    queryset = Message.objects.all()
    paginate_by = MESSAGES_PER_PAGE
    paginate_orphans = MESSAGES_PER_PAGE / 5


class FollowedView(ListView):
    template_name = 'board/followed.html'
    context_object_name = 'thread_list'
    allow_empty = True
    paginate_by = THREADS_PER_PAGE
    paginate_orphans = THREADS_PER_PAGE / 5


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if 'filter_unread' in kwargs:
            self.filter_unread = kwargs['filter_unread']
        else: 
            self.filter_unread = False
        return ListView.dispatch(self, *args, **kwargs)


    def get_queryset(self):
        queryset = Flag.objects.all().filter(user=self.request.user)
        if self.filter_unread:
            queryset = queryset.exclude(message=F('thread__last_message'))
        return queryset.order_by('thread__date_created')

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context['filter_unread'] = self.filter_unread
        return context

    def paginate_queryset(self, queryset, page_size):
        (paginator, page, object_list, is_paginated) = ListView.paginate_queryset(self, queryset, page_size)
        object_list = [x.thread for x in object_list]
        for thread in object_list:
            thread.annotate_flag(self.request.user)
        return (paginator, page, object_list, is_paginated)
