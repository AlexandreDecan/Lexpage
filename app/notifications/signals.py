import random

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from helpers.decorators import signal_ignore_fixture
from notifications.models import Notification


@receiver(post_delete, sender=Notification)
@receiver(post_save, sender=Notification)
@signal_ignore_fixture
def update_cached_etag(*args, **kwargs):
    username = kwargs['instance'].recipient.username
    cache.delete('etag-notifications-{}'.format(username))
