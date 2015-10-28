#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import re
from profile.models import ActiveUser


class Message(models.Model):
    user = models.ForeignKey(User, related_name='+')
    text = models.CharField(max_length=180, verbose_name='Message')
    date = models.DateTimeField(verbose_name='Heure', auto_now_add=True)

    def parse_anchors(self):
        """
        Parse current message, look for @anchor, and return a list of
        valid user that are targeted by such anchors.
        :return: List of users
        """
        candidates = [x[0] for x in re.findall(r'@([\w\-_]+)(\b|\W)', self.text)]

        # Filter valid candidates
        valid_candidates = set()
        for candidate in candidates:
            try:
                user = ActiveUser.objects.all().get(username__iexact=candidate)
                valid_candidates.add(user)
            except ActiveUser.DoesNotExist:
                pass

        return list(valid_candidates)

    def substitute(self):
        """
        If message is, eg. 's/from/to', replace every occurrence of 'from' by
        'to' in the last message of this author.
        :return: Unsaved modified message or None
        """
        match = re.match(r's/(.+)/(.*)', self.text)
        if match:
            try:
                # Get latest message for this author
                message = Message.objects.filter(user=self.user).latest()

                # Replace text
                message.text = message.text.replace(match.groups()[0], match.groups()[1])
                return message
            except Message.DoesNotExist:
                return None
        return None

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']
