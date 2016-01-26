from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import force_escape

from helpers.decorators import signal_ignore_fixture

from notifications.models import Notification

from .models import Slogan


@receiver(post_save, sender=Slogan)
@signal_ignore_fixture
def new_slogan_notification(sender, created, **kwargs):
    slogan = kwargs['instance']
    if created and not slogan.is_visible:
        recipients = User.objects.filter(groups__name='SloganTeam')
        for recipient in recipients:
            Notification.objects.get_or_create(
                    recipient=recipient,
                    title='Nouveau slogan',
                    description='Le slogan <em>%s</em> a été proposé par %s et doit être validé pour être visible.'
                                % (force_escape(slogan.slogan), slogan.author),
                    action=reverse('admin:slogan_slogan_changelist'),
                    app='slogan',
                    key=slogan.pk)


@receiver(post_save, sender=Slogan)
@signal_ignore_fixture
def remove_notifications_when_approved(sender, created, **kwargs):
    slogan = kwargs['instance']
    if not created and slogan.is_visible:
        if slogan.is_visible:
            Notification.objects.filter(app='slogan', key=slogan.pk).delete()


@receiver(post_delete, sender=Slogan)
def remove_notifications_when_deleted(sender, **kwargs):
    slogan = kwargs['instance']
    Notification.objects.filter(app='slogan', key=slogan.pk).delete()
