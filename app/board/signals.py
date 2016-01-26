from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from helpers.decorators import signal_ignore_fixture

from .models import Message, Flag


@receiver(post_save, sender=Message)
@signal_ignore_fixture
def update_thread_on_message_creation(sender, created, **kwargs):
    if created:
        message = kwargs['instance']
        message.thread.last_message = message
        message.thread.number += 1
        message.thread.save()


@receiver(pre_delete, sender=Message)
def update_thread_on_message_deletion(sender, **kwargs):
    message = kwargs['instance']

    previous = message.previous_message()
    if previous is None:
        Flag.objects.filter(thread=message.thread, message=message).delete()
    else:
        Flag.objects.filter(thread=message.thread, message=message).update(message=previous)

    thread = message.thread

    if thread.last_message == message:
        if previous is not None:
            thread.last_message = previous

    thread.number -= 1
    thread.save()


@receiver(post_delete, sender=Message)
def remove_empty_thread_on_message_deletion(sender, **kwargs):
    message = kwargs['instance']

    if message.thread.number == 0:
        message.thread.delete()
