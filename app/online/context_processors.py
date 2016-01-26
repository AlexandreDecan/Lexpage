from django.conf import settings
from helpers.request import is_incognito


def online_settings(request):
    return {
        'USER_IS_ONLINE_TIMEOUT': settings.USER_IS_ONLINE_TIMEOUT,
        'INCOGNITO': is_incognito(request),
    }
