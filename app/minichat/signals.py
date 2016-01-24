import json
import logging

from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

from helpers_redis import get_redis_publisher
from notifications.models import Notification

from .models import Message


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
def change_notifications_on_message_edition(sender, **kwargs):
    """
    If message has changed, remove the old uneeded notifications and add the new ones.
    """
    if not kwargs.get('raw', False): # check that this is not a fixture
        new_message = kwargs['instance']

        if new_message.id:
            old_message = Message.objects.get(pk=new_message.id)
            old_recipients = set(old_message.parse_anchors())
            new_recipients = set(new_message.parse_anchors())
            for recipient in old_recipients.difference(new_recipients):
                Notification.objects.filter(app='minichat', key=old_message.id, recipient=recipient).delete()
            for recipient in new_recipients.difference(old_recipients):
                create_minichat_notification(recipient, new_message)


@receiver(post_save, sender=Message)
def send_notifications_on_message_creation(sender, created, **kwargs):
    """
    On saving a new message, send notifications to involved users.
    """
    if not kwargs.get('raw', False): # check that this is not a fixture
        if created:
            message = kwargs['instance']
            anchors = message.parse_anchors()
            for anchor in anchors:
                create_minichat_notification(anchor, message)


@receiver(post_delete, sender=Message)
@receiver(post_save, sender=Message)
def send_minichat_update_message(sender, **kwargs):
    if not kwargs.get('raw', False): # check that this is not a fixture
        try:
            RedisPublisher = get_redis_publisher()
            redis_publisher = RedisPublisher(facility='lexpage', broadcast=True)
            message = {'action': 'reload_minichat', 'app': 'minichat'}
            redis_message = RedisMessage(json.dumps(message))
            redis_publisher.publish_message(redis_message)
        except ConnectionError:
            logger = logging.getLogger()
            logger.exception('Error when publishing a message to the websocket channel')

