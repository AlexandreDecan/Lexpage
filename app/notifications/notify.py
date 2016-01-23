from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import force_escape

from .models import Notification


def blog_pending_new(user, post):
    """
    Send a notification to every user in BlogTeam.
    """
    recipients = User.objects.filter(groups__name='BlogTeam')
    Notification.objects.get_or_create(
            recipients=recipients,
            title='Un billet est en attente de validation',
            description='Le billet <em>%s</em> proposé par %s est en attente de validation.' % (force_escape(post.title), post.author),
            action=reverse('blog_pending_edit', kwargs={'pk': post.pk}),
            app='blog',
            key='pending-%d' % post.pk)


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
        Notification.objects.get_or_create(
                recipient=post.author,
                title='Votre billet a été accepté',
                description='Le billet <em>%s</em> que vous avez proposé a été accepté par %s et sera prochainement publié.'
                             % (force_escape(post.title), user.get_username()),
                app='blog',
                key='validate-%d' % post.pk)


def blog_pending_delete(user, post):
    """
    Warn the author that his post has been rejected EXCEPT if author = user.
    """
    blog_pending_clean(user, post)
    if post.author != user:
        Notification.objects.get_or_create(
                recipient=post.author,
                title='Votre billet a été refusé',
                description='Le billet <em>%s</em> que vous avez proposé a été refusé par %s.'
                             % (force_escape(post.title), user.get_username()),
                app='blog',
                key='validate-%d' % post.pk)


def messaging_thread_new(user, thread):
    """
    Notify the participants (except the author) that a new thread is
    created.
    """
    recipients = thread.recipients
    recipients.remove(user)
    Notification.objects.get_or_create(
            recipients=recipients,
            title='Nouvelle conversation',
            description='%s a entamé une nouvelle conversation avec vous : <em>%s</em>.'
                         % (user.get_username(), force_escape(thread.title)),
            action=reverse('messaging_show', kwargs={'thread': thread.pk}),
            app='messaging',
            key='thread-%d' % thread.pk)


def messaging_mesage_new(user, thread):
    """
    Notify the participants (except the author) that a new message has
    been posted, except if a notification for a new thread is pending.
    """
    recipients = thread.recipients
    recipients.remove(user)
    Notification.objects.get_or_create(
            recipients=recipients,
            title='Nouveau message',
            description='%s a posté un nouveau message dans la conversation <em>%s</em>.'
                         % (user.get_username(), force_escape(thread.title)),
            action=reverse('messaging_show', kwargs={'thread': thread.pk})+'#unread',
            app='messaging',
            key='thread-%d' % thread.pk)


def board_post_moderate(user, message):
    """
    Notify the user that his post has been moderated.
    """
    Notification.objects.get_or_create(
            recipient=message.author,
            title='Message modéré',
            description='L\'un de vos messages a été modéré par %s dans la discussion <em>%s</em>.'
                         % (user.get_username(), force_escape(message.thread.title)),
            action=reverse('board_message_show', kwargs={'message': message.pk}),
            app='board',
            key='thread-%d' % message.thread.pk)


def profile_new(user):
    """
    Send a notification to welcome a newly created user.
    """
    Notification.objects.get_or_create(
            recipient=user,
            title='Bienvenue sur Lexpage',
            description='Bienvenue sur Lexpage. Pensez à compléter votre profil et à choisir un avatar !',
            action=reverse('profile_edit'),
            app='profile',
            key='new')


