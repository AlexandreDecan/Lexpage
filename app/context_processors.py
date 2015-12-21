from django.conf import settings
from django.contrib.sites.models import Site


def site(request):
    return {
        'site': Site.objects.get_current()
    }


def global_settings(request):
    # return any necessary values
    return {
        'DEFAULT_THEME': settings.THEMES['DEFAULT'],
        'THEMES': settings.THEMES['ALL'],
    }
