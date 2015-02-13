#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django import forms
from models import Message

class MessageForm(forms.ModelForm):

    class Meta():
        model = Message
        fields = ('text', )
