#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from models import Slogan 
from forms import SloganAddForm
from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from notifications import notify


class SloganListView(ListView):
    queryset = Slogan.visible.all()
    template_name = 'slogan/list.html'
    context_object_name = 'slogan_list'
    paginate_by = 30
    paginate_orphans = 6

    def get_context_data(self, **kwargs):
        kwargs['form']= SloganAddForm
        return super(SloganListView, self).get_context_data(**kwargs)


class SloganAddView(CreateView):
    form_class = SloganAddForm
    template_name = 'slogan/list.html'


    dispatch = method_decorator(login_required)(CreateView.dispatch)


    def form_valid(self, form):
        user = self.request.user
        
        author = user.username
        slogan = form.cleaned_data['slogan']
        obj_slogan = Slogan(author=author, slogan=slogan, is_visible=False)
        obj_slogan.save()

        notify.slogan_new(user, obj_slogan)
        messages.success(self.request, 'Votre slogan a été enregistré. Il sera visible en ligne prochainement.')
        
        return redirect('slogan_list')


    def form_invalid(self, form):
        messages.error(self.request, 'Le formulaire n\'a pas été complété correctement.')
        return redirect('slogan_list')
        


