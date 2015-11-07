import os

# Environment variable must be defined before importing whitenoise
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()

# Serve static files using Python, for testing purposes
application = DjangoWhiteNoise(application)
