from django.conf import settings

def global_settings(request):
    # return any necessary values
    return {
        'DEFAULT_THEME': settings.DEFAULT_THEME,
    }
