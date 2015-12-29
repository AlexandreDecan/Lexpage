from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message
from redis_helpers import get_redis_publisher
from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

@receiver(post_delete, sender=Message)
@receiver(post_save, sender=Message)
def send_minichat_update_message(sender, **kwargs):
    try:
        RedisPublisher = get_redis_publisher()
        redis_publisher = RedisPublisher(facility='minichat', broadcast=True)
        redis_message = RedisMessage('new-message')
        redis_publisher.publish_message(redis_message)
    except ConnectionError:
        pass

