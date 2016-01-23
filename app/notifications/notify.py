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


