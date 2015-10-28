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

    class Meta():
        get_latest_by = 'date'
        ordering = ['date']
