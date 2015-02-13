#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django import forms
from models import Message, Thread


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'markup-bbcode'})

    class Meta():
        model = Message
        fields = ('text',)


class MessageModerateForm(forms.ModelForm):
    MODERATE_CHOICES = (
        (False, 'Modifier le message'),
        (True, 'Modérer le message')
    )
    moderated = forms.ChoiceField(required=True, label='Action', choices=MODERATE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(MessageModerateForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'markup-bbcode'})
        # self.fields['moderated'].widget = forms.HiddenInput()

    def clean_moderated(self):
        if self.cleaned_data['moderated'] == 'True':
            return True
        else:
            return False

    class Meta():
        model = Message
        fields = ('text', 'moderated')



class ThreadForm(forms.ModelForm):
    title = forms.CharField(max_length=80, required=True, label='Sujet de la discussion')

    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'markup-bbcode'})


    class Meta():
        model = Message
        fields = ('title', 'text',)
