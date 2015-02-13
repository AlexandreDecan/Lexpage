#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.http import HttpResponse
from django.views.generic import View, RedirectView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from models import Notification


class DismissView(View):
    dispatch = method_decorator(login_required)(View.dispatch)

    def get(self, request, **kwargs):
        notification = get_object_or_404(Notification.objects, pk=kwargs['pk'], recipient=request.user.pk)
        notification.dismiss()
        return HttpResponse('')



class ShowView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(View.dispatch)

    def get_redirect_url(self, **kwargs):
        notification = get_object_or_404(Notification.objects, pk=kwargs['pk'], recipient=self.request.user.pk)
        notification.dismiss()
        return notification.action
