#!/usr/bin/python
# coding=utf-8

from django.test import TestCase
import operator
from minichat.models import Message
from django.contrib.auth.models import User


class AnchorTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()

        # We need at least 2 users
        self.assertGreaterEqual(len(self.users), 2)

    def test_single(self):
        anchor = self.users[1]
        formats = [
            'Hello @{}!',
            'Hello@{}!',
            '@{}',
            '@@{}',
            '@{}@',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchor.get_username()))
            self.assertListEqual(message.parse_anchors(), [anchor], msg='format: %s' % frmt)

    def test_multiple(self):
        anchors = map(operator.methodcaller('get_username'), self.users[:2])
        formats = [
            'Hello @{0} @{1}',
            '@{0}@{1}',
            '@{0}@{0}@{1}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchors[0].get_username(), anchors[1].get_username()))
            self.assertListEqual(message.parse_anchors(), anchors, msg='format: %s' % frmt)

    def test_invalid(self):
        anchors = map(operator.methodcaller('get_username'), self.users[:2])
        formats = [
            '@{0}abcdefghijklmnopqrstuvwxyz', # ... and expect this is not a valid username
            '{0}@{1}.com',
            '@ {0}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchors[0].get_username(), anchors[1].get_username()))
            self.assertListEqual(message.parse_anchors(), [], msg='format: %s' % frmt)
