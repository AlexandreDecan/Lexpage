from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from helpers.decorators import signal_ignore_fixture

from .models import Profile


@receiver(post_save, sender=User)
@signal_ignore_fixture
def create_profile_for_user(sender, **kwargs):
    """
    Post save signal handler for User model. Add a Profile instance to any newly created
    User instance.
    """
    if kwargs.get('created', False):
        profile, is_new = Profile.objects.get_or_create(user=kwargs['instance'])
        if is_new:
            profile.save()
