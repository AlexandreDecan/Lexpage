from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import force_escape

from .models import Notification


def notify(recipients, title, description, action, app, key):
    """
    Send a notification to given recipient with a title, description, action,
    app name and key. Description and action can be None. If recipient is
    an iterable, then send the notification to each of the recipients.
    The notification is not added if a similar notification (with app and key)
    exists for the recipient.

    Return the number of notifications sent.
    """

    description = '' if description is None else description
    action = '' if action is None else action
    if not hasattr(recipients, '__iter__'):
        recipients = [recipients]

    nb = 0  # number of notifications sent
    for recipient in recipients:
        # Is there a notification?
        try:
            Notification.objects.get(app=app, key=key, recipient=recipient)
        except Notification.DoesNotExist:
            # Create a new notification and save it
            n = Notification(title=title, description=description, action=action,
                             recipient=recipient, app=app, key=key)
            nb += 1
            n.save()
    return nb


def delete_notification(recipients, app, key):
    """
    Remove a notification
    We call delete and not dismiss because the goal is really to delete notification.
    """

    if not hasattr(recipients, '__iter__'):
        recipients = [recipients]

    nb = 0  # number of notifications deleted
    for recipient in recipients:
        # Is there a notification?
        try:
            Notification.objects.get(app=app, key=key, recipient=recipient).delete()
            nb += 1
        except Notification.DoesNotExist:
            # The notification was already dismissed
            pass
    return nb


def escape(string):
    return force_escape(string)


def blog_pending_new(user, post):
    """
    Send a notification to every user in BlogTeam.
    """
    recipients = User.objects.filter(groups__name='BlogTeam')
    notify(recipients, 'Un billet est en attente de validation',
           'Le billet <em>%s</em> proposé par %s est en attente de validation.' % (escape(post.title), post.author),
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
        notify(post.author, 'Votre billet a été accepté',
               'Le billet <em>%s</em> que vous avez proposé a été accepté par %s et sera prochainement publié.'
               % (escape(post.title), user.get_username()),
               None, 'blog', 'validate-%d' % post.pk)


def blog_pending_delete(user, post):
    """
    Warn the author that his post has been rejected EXCEPT if author = user.
    """
    blog_pending_clean(user, post)
    if post.author != user:
        notify(post.author, 'Votre billet a été refusé',
               'Le billet <em>%s</em> que vous avez proposé a été refusé par %s.'
               % (escape(post.title), user.get_username()),
               None, 'blog', 'validate-%d' % post.pk)


def messaging_thread_new(user, thread):
    """
    Notify the participants (except the author) that a new thread is
    created.
    """
    recipients = thread.recipients
    recipients.remove(user)
    notify(recipients, 'Nouvelle conversation',
           '%s a entamé une nouvelle conversation avec vous : <em>%s</em>.'
           % (user.get_username(), escape(thread.title)),
           reverse('messaging_show', kwargs={'thread': thread.pk}), 'messaging', 'thread-%d' % thread.pk)


def messaging_mesage_new(user, thread):
    """
    Notify the participants (except the author) that a new message has
    been posted, except if a notification for a new thread is pending.
    """
    recipients = thread.recipients
    recipients.remove(user)
    notify(recipients, 'Nouveau message',
           '%s a posté un nouveau message dans la conversation <em>%s</em>.'
           % (user.get_username(), escape(thread.title)),
           reverse('messaging_show', kwargs={'thread': thread.pk})+'#unread', 'messaging', 'thread-%d' % thread.pk)


def board_post_moderate(user, message):
    """
    Notify the user that his post has been moderated.
    """
    notify(message.author, 'Message modéré',
           'L\'un de vos messages a été modéré par %s dans la discussion <em>%s</em>.'
           % (user.get_username(), escape(message.thread.title)),
           reverse('board_message_show', kwargs={'message': message.pk}), 'board', 'thread-%d' % message.thread.pk)


def profile_new(user):
    """
    Send a notification to welcome a newly created user.
    """
    notify(user, 'Bienvenue sur Lexpage',
           'Bienvenue sur Lexpage. Pensez à compléter votre profil et à choisir un avatar !',
           reverse('profile_edit'), 'profile', 'new')


def slogan_new(user, slogan):
    """
    Send a notification to every user that is in SloganTeam
    that a new slogan has been posted.
    """
    recipients = User.objects.filter(groups__name='SloganTeam')
    notify(recipients, 'Nouveau slogan',
           'Le slogan <em>%s</em> a été proposé par %s et doit être validé pour être visible.'
           % (escape(slogan.slogan), user.get_username()),
           reverse('admin:slogan_slogan_changelist'), 'slogan', slogan.pk)


def minichat_unwarn(user, message):
    """
    Remove a notification for the user and the minichat.
    """
    delete_notification(user, 'minichat', message.pk)

def minichat_warn(user, message):
    """
    Send a notification to target user to warn him that someone has
    said his name in the minichat.
    """
    # The following line is commented because it leads to a tiny bug. Indeed, len(urlize3(text) could be greater
    # than len(text), and sometimes greater than 255 chars which is a pain for the field in db and possibly leads to
    # a truncated <a> when displayed.
    # text = smiley(urlize3(message.text))
    text = message.text
    notify(user,
           'Minichat', '%s vous a adressé un message : <br/><em>%s</em>' % (message.user, text),
           message.get_absolute_url(),
           'minichat',
           message.pk)
