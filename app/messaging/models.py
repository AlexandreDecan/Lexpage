#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

import datetime


class ThreadManager(models.Manager):
    def createThread(self, user, title, text, targets):
        """ Create a new thread with the given title and post
        a message with given text inside. Create and update 
        targets' MessageBoxes (and user's one) accordingly. 
        Return the newly created user's MessageBox. """
        
        # Empty title -> autopopulate!
        if len(title) == 0:
            usernames = [user.get_username()] + [x.get_username() for x in targets]
            usernames.sort()
            title = 'Conversation entre %s et %s' % (', '.join(usernames[:-1]), usernames[-1])

        # Create thread
        thread = Thread(title=title)
        thread.save()   # Needed to have a PK value

        # Create user's message box
        userMBox = MessageBox(user=user, thread=thread)
        userMBox.save()

        # Create MessageBoxes for targets
        for target in targets:
            targetMBox = MessageBox(user=target, thread=thread)
            targetMBox.save()

        # Post message
        thread.postMessage(user, text)
        return userMBox




class Thread(models.Model):
    title = models.CharField(verbose_name='Titre', max_length=60)
    last_message = models.ForeignKey('Message', verbose_name='Dernier message', related_name='+', default=-1)

    objects = ThreadManager()

    class Meta():
        get_latest_by = 'last_message'
        ordering = ['-last_message__date']
        verbose_name = 'Conversation'

    def __unicode__(self):
        return self.title

    def get_recipients(self):
        boxes = MessageBox.objects.all().filter(thread=self)
        users = []
        for box in boxes:
            users.append(box.user)
        users.sort(key=lambda x: x.username)
        return users

    def number(self):
        return Message.objects.all().filter(thread=self).count()

    def postMessage(self, user, text):
        """ Post a message in the current thread and update
        the MessageBoxes according to their status. 
        Return user's MessageBox. """
        # Create message
        message = Message(author=user, thread=self, text=text)
        message.save()

        self.last_message = message
        self.save()

        # Update MessageBoxes
        messageBoxes = MessageBox.objects.filter(thread=self)
        for messageBox in messageBoxes:
            if messageBox.status == MessageBox.STATUS_DELETED:
                messageBox.mark_normal()
            elif messageBox.status == MessageBox.STATUS_ARCHIVED:
                messageBox.mark_normal()
            messageBox.save()

        # Update current user MessageBox's date_read
        messageBox = MessageBox.objects.get(user=user, thread=self)
        messageBox.mark_read()
        messageBox.save()

        return messageBox



class Message(models.Model):
    author = models.ForeignKey(User, verbose_name='Auteur', related_name='+')
    thread = models.ForeignKey(Thread, verbose_name='Conversation')
    text = models.TextField(verbose_name='Message')
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)

    def __unicode__(self):
        return self.text

    class Meta():
        get_latest_by = 'date'
        ordering = ['date']
        verbose_name = 'Message'



class MessageBoxManager(models.Manager):
    def __init__(self, status):
        super(MessageBoxManager, self).__init__()
        self._status = status

    def get_queryset(self):
        return super(MessageBoxManager, self).get_queryset().filter(status=self._status)


class MessageBox(models.Model):
    DEFAULT_UNREAD_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)

    STATUS_DELETED = -1
    STATUS_NORMAL = 1
    STATUS_ARCHIVED = 2

    STATUS_CHOICES = (
        (STATUS_NORMAL, 'Normal'),
        (STATUS_ARCHIVED, 'Archivée'),
        (STATUS_DELETED, 'Supprimée'),
    )

    user = models.ForeignKey(User, verbose_name='Propriétaire')
    thread = models.ForeignKey(Thread, verbose_name='Conversation')
    date_read = models.DateTimeField(verbose_name='Dernière lecture', default=DEFAULT_UNREAD_DATE)
    is_starred = models.BooleanField(verbose_name='Favorites ?', default=False)
    status = models.SmallIntegerField(verbose_name='État', choices=STATUS_CHOICES, default=STATUS_NORMAL)

    objects = models.Manager()
    archived = MessageBoxManager(STATUS_ARCHIVED)
    unarchived = MessageBoxManager(STATUS_NORMAL)

    class Meta():
        ordering = ['-thread__last_message__date']
        verbose_name = 'Boîte de réception'
        verbose_name_plural = 'Boîtes de réceptions'

    def __unicode__(self):
        return '%s: %s' % (self.user, self.thread)

    def is_read(self):
        return self.thread.last_message.date <= self.date_read
        
    def is_archived(self):
        return self.status == MessageBox.STATUS_ARCHIVED

    def mark_read(self):
        self.date_read = now()
        self.save()

    def mark_unread(self):
        self.date_read = MessageBox.DEFAULT_UNREAD_DATE
        self.save()

    def mark_starred(self):
        self.is_starred = True
        self.save()

    def mark_unstarred(self):
        self.is_starred = False
        self.save()

    def mark_normal(self):
        self.status = MessageBox.STATUS_NORMAL
        self.save()

    def mark_archived(self):
        self.status = MessageBox.STATUS_ARCHIVED
        self.save()

    def mark_deleted(self):
        # Mark as deleted
        self.is_starred = False
        self.status = MessageBox.STATUS_DELETED
        self.save()

        # Get MessageBoxes
        messageBoxes = MessageBox.objects.filter(thread=self.thread)

        # If every authors' MessageBox for this Thread is 
        # STATUS_DELETED, then remove everything related...
        for messageBox in messageBoxes:
            if messageBox.status != MessageBox.STATUS_DELETED: 
                return
        # Removing the thread will normally do the job...
        self.thread.delete()
