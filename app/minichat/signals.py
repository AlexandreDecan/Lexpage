import json
import logging

from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

from redis_helpers import get_redis_publisher
from notifications import notify

from .models import Message

@receiver(pre_delete, sender=Message)
@receiver(pre_save, sender=Message)
def remove_notifications(sender, **kwargs):
    """ Before Saving and Deleting, remove notifications.
    If needed, they will be added again in post_save."""
    if not kwargs.get('raw', False):
        message = kwargs['instance']
        # If the message existed, use the existing one
        if message.id:
            message = Message.objects.get(pk=message.id)
        anchors = message.parse_anchors()
        for anchor in anchors:
            notify.minichat_unwarn(anchor, message)


@receiver(post_save, sender=Message)
def send_notifications(sender, **kwargs):
    """ Before Saving and Deleting, remove notifications.
    If needed, they will be added again in post_save."""
    if not kwargs.get('raw', False):
        message = kwargs['instance']
        anchors = message.parse_anchors()
        for anchor in anchors:
            notify.minichat_warn(anchor, message)


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

