import random

from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache

from helpers.decorators import signal_ignore_fixture
from notifications.models import Notification

from .models import Message


@receiver(post_delete, sender=Message)
@receiver(post_save, sender=Message)
@signal_ignore_fixture
def update_cached_etag(*args, **kwargs):
    cache.delete('cache-minichat')


def create_minichat_notification(user, message):
    """
    Send a notification to target user to warn him that someone has
    said his name in the minichat.
    """
    # The following line is commented because it leads to a tiny bug. Indeed, len(urlize3(text) could be greater
    # than len(text), and sometimes greater than 255 chars which is a pain for the field in db and possibly leads to
    # a truncated <a> when displayed.
    # text = smiley(urlize3(message.text))
    text = message.text
    Notification.objects.get_or_create(
            recipient=user,
            title='Minichat',
            description='%s vous a adressé un message : <br/><em>%s</em>' % (message.user, text),
            action=message.get_absolute_url(),
            app='minichat',
            key=message.pk
    )


@receiver(pre_delete, sender=Message)
def remove_notifications_on_message_deletion(sender, **kwargs):
    """
    Before deletion, remove notifications.
    """

    message = kwargs['instance']
    # Remove notifications if any
    Notification.objects.filter(app='minichat', key=message.id).delete()


@receiver(pre_save, sender=Message)
@signal_ignore_fixture
def change_notifications_on_message_edition(sender, **kwargs):
    """
    If message has changed, remove the old uneeded notifications and add the new ones.
    """
    new_message = kwargs['instance']

    if new_message.id:
        old_message = Message.objects.get(pk=new_message.id)
        old_recipients = set(old_message.parse_anchors())
        new_recipients = set(new_message.parse_anchors())

        # Delete notifications for recipients that were removed
        for recipient in old_recipients.difference(new_recipients):
            try:
                Notification.objects.get(app='minichat', key=old_message.id, recipient=recipient).delete()
            except Notification.DoesNotExist:
                pass

        # Recreate notifications for recipients that still have the notification
        #   because notification text must be adapted.
        for recipient in new_recipients.intersection(old_recipients):
            try:
                Notification.objects.get(app='minichat', key=old_message.id, recipient=recipient).delete()
                create_minichat_notification(recipient, new_message)
            except Notification.DoesNotExist:
                pass

        # Create notifications for recipients that were added
        for recipient in new_recipients.difference(old_recipients):
            create_minichat_notification(recipient, new_message)



@receiver(post_save, sender=Message)
@signal_ignore_fixture
def send_notifications_on_message_creation(sender, created, **kwargs):
    """
    On saving a new message, send notifications to involved users.
    """
    if created:
        message = kwargs['instance']
        anchors = message.parse_anchors()
        for anchor in anchors:
            create_minichat_notification(anchor, message)