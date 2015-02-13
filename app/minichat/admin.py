#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from models import Message


class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('user', 'text', 'date')
    search_field = ('user__username', 'text')
    ordering = ('-date',)
    date_hierarchy = 'date'
    list_editable = ('text',)

admin.site.register(Message, MessageAdmin)
