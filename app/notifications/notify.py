#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.template.defaultfilters import force_escape

from models import Notification
from minichat.templatetags.minichat import urlize3
from commons.templatetags.markup_bbcode import smiley 

import datetime


def notify(recipients, title, description, action, app, key):
    """
    Send a notification to given recipient with a title, description, action, 
    app name and key. Description and action can be None. If recipient is 
    an iterable, then send the notification to each of the recipients. 
    The notification is not added if a similar notification (with app and key)
    exists for the recipient. 

    Return the number of notifications sent. 
    """

    description = '' if description == None else description
    action = '' if action == None else action
    if not hasattr(recipients, '__iter__'):
        recipients = [recipients]

    nb = 0  # number of notifications sent
    for recipient in recipients:
        # Is there a notification? 
        try:
            Notification.objects.get(app=app, key=key, recipient=recipient)
        except Notification.DoesNotExist as e: 
            # Create a new notification and save it
            n = Notification(title=title, description=description, action=action, 
                         recipient=recipient, app=app, key=key)
            nb += 1
            n.save()
    return nb


def escape(string):
    return force_escape(string)


def blog_draft_new(user, post):
    """
    Send a notification to every user in BlogTeam. 
    """
    recipients = User.objects.filter(groups__name='BlogTeam')
    notify(recipients, 'Un billet est en attente de validation', 'Le billet <em>%s</em> proposé par %s est en attente de validation.' % (escape(post.title), post.author),
           reverse('blog_pending_edit', kwargs={'pk': post.pk}), 'blog', 'pending-%d' % post.pk)


def blog_pending_clean(user, post):
    """
    Remove the notifications related to the post that had been handled. 
    """
    Notification.objects.filter(app='blog', key='pending-%d' % post.pk).delete()  


def blog_pending_approve(user, post):
    """
    Warn the author that his post has been accepted EXCEPT if author = user.
    """
    blog_pending_clean(user, post)
    if post.author != user:
        notify(post.author, 'Votre billet a été accepté', 'Le billet <em>%s</em> que vous avez proposé a été accepté par %s et sera prochainement publié.' % (escape(post.title), user.get_username()),
           None, 'blog', 'validate-%d' % post.pk)


def blog_pending_delete(user, post):
    """
    Warn the author that his post has been rejected EXCEPT if author = user. 
    """
    blog_pending_clean(user, post)
    if post.author != user:
        notify(post.author, 'Votre billet a été refusé', 'Le billet <em>%s</em> que vous avez proposé a été refusé par %s.' % (escape(post.title), user.get_username()),
           None, 'blog', 'validate-%d' % post.pk)    


def messaging_thread_new(user, thread):
    """
    Notify the participants (except the author) that a new thread is 
    created. 
    """
    recipients = thread.get_recipients()
    recipients.remove(user)
    notify(recipients, 'Nouvelle conversation', '%s a entamé une nouvelle conversation avec vous : <em>%s</em>.' % (user.get_username(), escape(thread.title)),
           reverse('messaging_show', kwargs={'thread': thread.pk}), 'messaging', 'thread-%d' % thread.pk)


def messaging_mesage_new(user, thread):
    """
    Notify the participants (except the author) that a new message has
    been posted, except if a notification for a new thread is pending. 
    """
    recipients = thread.get_recipients()
    recipients.remove(user)
    notify(recipients, 'Nouveau message', '%s a posté un nouveau message dans la conversation <em>%s</em>.' % (user.get_username(), escape(thread.title)),
           reverse('messaging_show', kwargs={'thread': thread.pk})+'#unread', 'messaging', 'thread-%d' % thread.pk)


def board_post_moderate(user, message):
    """
    Notify the user that his post has been moderated. 
    """
    notify(message.author, 'Message modéré', 'L\'un de vos messages a été modéré par %s dans la discussion <em>%s</em>.' % (user.get_username(), escape(message.thread.title)), 
           reverse('board_message_show', kwargs={'message': message.pk}), 'board', 'thread-%d' % message.thread.pk)


def profile_new(user):
    """ 
    Send a notification to welcome a newly created user.
    """
    notify(user, 'Bienvenue sur Lexpage', 'Bienvenue sur Lexpage. Pensez à compléter votre profil et à choisir un avatar !',
           reverse('profile_edit'), 'profile', 'new')


def slogan_new(user, slogan):
    """
    Send a notification to every user that is in SloganTeam
    that a new slogan has been posted. 
    """
    recipients = User.objects.filter(groups__name='SloganTeam')
    notify(recipients, 'Nouveau slogan', 'Le slogan <em>%s</em> a été proposé par %s et doit être validé pour être visible.' % (escape(slogan.slogan), user.get_username()),
           reverse('admin:slogan_slogan_changelist'), 'slogan', slogan.pk)

def minichat_warn(user, message):
    """
    Send a notification to target user to warn him that someone has 
    said his name in the minichat. 
    """

    year = message.date.year
    month = message.date.month
    dayhourminute = message.date.strftime('%d%H%M')
    texte = smiley(urlize3(message.text))
    notify(user, 'Minichat', '%s vous a adressé un message : <br/><em>%s</em>' % (message.user, texte),
           reverse('minichat_archives', kwargs={'year':year, 'month':month})+('#%s%s%s' % (dayhourminute[0:2], dayhourminute[2:4], dayhourminute[4:6])), 'minichat', message.pk)
