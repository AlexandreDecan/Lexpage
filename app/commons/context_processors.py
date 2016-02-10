from django.conf import settings
from helpers.request import is_incognito


def online_settings(request):
    return {
        'USER_IS_ONLINE_TIMEOUT': settings.USER_IS_ONLINE_TIMEOUT,
        'INCOGNITO': is_incognito(request),
    }


def global_settings(request=None):
    # return any necessary values
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DEMONYM': settings.SITE_DEMONYM,
        'SITE_SCHEME': settings.SITE_SCHEME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,

        'THEMES': settings.THEMES,
        'ANALYTICS': settings.ANALYTICS,
    }
