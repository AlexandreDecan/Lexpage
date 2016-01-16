from django.conf import settings
from django.contrib.sites.models import Site



def global_settings(request):
    # return any necessary values
    return {
        'site': Site.objects.get_current(),
        'THEMES': settings.THEMES,
        'ANALYTICS': settings.ANALYTICS,
        'SITENAME': settings.SITENAME,
        'DEMONYM': settings.DEMONYM,
        'ENABLE_WEBSOCKET': settings.ENABLE_WEBSOCKET,
    }
