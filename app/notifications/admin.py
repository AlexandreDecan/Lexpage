#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from models import Notification

class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    list_display = ('title', 'app', 'recipient', 'date')
    search_field = ('app', 'key', 'title')
    date_hierarchy = 'date'


admin.site.register(Notification, NotificationAdmin)
