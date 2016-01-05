import json

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from redis_helpers import get_redis_publisher
from ws4redis.redis_store import RedisMessage
from redis.exceptions import ConnectionError

@receiver(post_delete, sender=Notification)
@receiver(post_save, sender=Notification)
def send_notification_update_message(sender, **kwargs):
    try:
        RedisPublisher = get_redis_publisher()
        notification = kwargs.get('instance')
        redis_publisher = RedisPublisher(facility='lexpage', users=[notification.recipient])
        counter = str(len(sender.objects.filter(recipient__id=notification.recipient.id)))
        message = {'action': 'update_counter', 'data': counter, 'app': 'notifications'}
        redis_message = RedisMessage(json.dumps(message))
        redis_publisher.publish_message(redis_message)
    except ConnectionError:
        pass

