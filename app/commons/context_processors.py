from django.conf import settings
from django.contrib.sites.models import Site
from helpers.request import is_incognito


def online_settings(request):
    return {
        'USER_IS_ONLINE_TIMEOUT': settings.USER_IS_ONLINE_TIMEOUT,
        'INCOGNITO': is_incognito(request),
    }


def global_settings(request):
    # return any necessary values
    return {
        'site': Site.objects.get_current(),
        'THEMES': settings.THEMES,
        'ANALYTICS': settings.ANALYTICS,
        'SITENAME': settings.SITENAME,
        'DEMONYM': settings.DEMONYM,
    }
