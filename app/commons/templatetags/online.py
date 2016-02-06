from django import template
from profile.models import ActiveUser
from django.conf import settings

import datetime

register = template.Library()


def who_is_online():
    absolute_timeout = datetime.datetime.now() - datetime.timedelta(minutes=settings.USER_IS_ONLINE_TIMEOUT)
    users = ActiveUser.objects.filter(is_active=True, profile__last_visit__gt=absolute_timeout)
    return users

register.assignment_tag(who_is_online)
