import os

# Environment variable must be defined before importing whitenoise
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()