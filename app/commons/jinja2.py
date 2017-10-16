from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.conf import settings

from django.utils import datetime_safe
from django.template import defaultfilters
from django.contrib.humanize.templatetags import humanize

from jinja2 import Environment

from commons.templatetags import flatpageblock, online
from notifications.templatetags import notifications
from slogan.templatetags import slogan
from profile.templatetags import birthday


def reverse_url(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)


def environment(**options):
    env = Environment(**options)

    env.globals.update({
        'USER_IS_ONLINE_TIMEOUT': settings.USER_IS_ONLINE_TIMEOUT,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DEMONYM': settings.SITE_DEMONYM,
        'SITE_SCHEME': settings.SITE_SCHEME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,

        'THEMES': settings.THEMES,
        'ANALYTICS': settings.ANALYTICS,

        'flatpageblock': flatpageblock.flatpageblock,
        'who_is_online': online.who_is_online,
        'notifications': notifications.notifications,
        'random_slogan': slogan.random_slogan,
        'birthday': birthday.birthday,

        'static': staticfiles_storage.url,
        'url': reverse_url,
        'now': lambda f: defaultfilters.date(datetime_safe.datetime.now(), f),
    })

    env.filters.update({
        'date': defaultfilters.date,
        'naturalday': humanize.naturalday,
    })

    return env

