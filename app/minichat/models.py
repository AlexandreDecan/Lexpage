#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User



class Message(models.Model):
    user = models.ForeignKey(User, related_name='+')
    text = models.CharField(max_length=180, verbose_name='Message')
    date = models.DateTimeField(verbose_name='Heure', auto_now_add=True)

    class Meta():
        get_latest_by = 'date'
        ordering = ['date']
