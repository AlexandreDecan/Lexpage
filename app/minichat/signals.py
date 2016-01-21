import json
import logging

from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

from redis_helpers import get_redis_publisher
from notifications.notify import minichat_warn
from notifications.models import Notification

from .models import Message


@receiver(pre_delete, sender=Message)
def remove_notifications(sender, **kwargs):
    """
    Before deletion, remove notifications.
    """

    message = kwargs['instance']
    # Remove notifications if any
    Notification.objects.filter(app='minichat', key=message.id).delete()


@receiver(pre_save, sender=Message)
def change_notifications(sender, **kwargs):
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
                minichat_warn(recipient, new_message)


@receiver(post_save, sender=Message)
def send_notifications(sender, created, **kwargs):
    """
    On saving a new message, send notifications to involved users.
    """
    if not kwargs.get('raw', False): # check that this is not a fixture
        if created:
            message = kwargs['instance']
            anchors = message.parse_anchors()
            for anchor in anchors:
                minichat_warn(anchor, message)


@receiver(post_delete, sender=Message)
@receiver(post_save, sender=Message)
def send_minichat_update_message(sender, **kwargs):
    try:
        RedisPublisher = get_redis_publisher()
        redis_publisher = RedisPublisher(facility='lexpage', broadcast=True)
        message = {'action': 'reload_minichat', 'app': 'minichat'}
        redis_message = RedisMessage(json.dumps(message))
        redis_publisher.publish_message(redis_message)
    except ConnectionError:
        logger = logging.getLogger()
        logger.exception('Error when publishing a message to the websocket channel')

