from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from helpers.decorators import signal_ignore_fixture
from notifications.models import Notification

