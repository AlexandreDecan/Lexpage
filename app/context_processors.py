from django.conf import settings

def global_settings(request):
    # return any necessary values
    return {
        'DEFAULT_THEME': settings.THEMES['DEFAULT'],
        'THEMES': settings.THEMES['ALL'],
    }
