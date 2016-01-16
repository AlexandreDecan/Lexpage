import json
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

from redis_helpers import get_redis_publisher

from .models import Message

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

