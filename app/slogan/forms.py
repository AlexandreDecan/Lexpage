#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django import forms
from models import Slogan


class SloganAddForm(forms.ModelForm):
    
    class Meta():
        model = Slogan
        fields = ('slogan',)
