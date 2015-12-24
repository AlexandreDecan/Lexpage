from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from redis_helpers import get_redis_publisher
from ws4redis.redis_store import RedisMessage

@receiver(post_delete, sender=Notification)
@receiver(post_save, sender=Notification)
def send_notification_update_message(sender, **kwargs):
    RedisPublisher = get_redis_publisher()
    notification = kwargs.get('instance')
    redis_publisher = RedisPublisher(facility='notifications', users=[notification.recipient])
    redis_message = RedisMessage(str(len(sender.objects.filter(recipient__id=notification.recipient.id))))
    redis_publisher.publish_message(redis_message)

