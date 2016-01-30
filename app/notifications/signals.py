import json
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

from helpers.decorators import signal_ignore_fixture
from helpers.redis import get_redis_publisher

from .models import Notification


@receiver(post_delete, sender=Notification)
@receiver(post_save, sender=Notification)
@signal_ignore_fixture
def send_notification_update_message(sender, **kwargs):
    try:
        RedisPublisher = get_redis_publisher()
        notification = kwargs.get('instance')
        redis_publisher = RedisPublisher(facility='lexpage', users=[notification.recipient])

        counter = str(len(sender.objects.filter(recipient__id=notification.recipient.id)))
        message = {'action': 'update_counter', 'data': counter, 'app': 'notifications'}
        redis_message = RedisMessage(json.dumps(message))
        redis_publisher.publish_message(redis_message)

        if notification.app == 'minichat' and not 'raw' in kwargs: # only when deleting minichat notifications
            message = {'action': 'reload_minichat', 'app': 'minichat'}
            redis_message = RedisMessage(json.dumps(message))
            redis_publisher.publish_message(redis_message)

    except ConnectionError:
        logger = logging.getLogger()
        logger.exception('Error when publishing a message to the websocket channel')
