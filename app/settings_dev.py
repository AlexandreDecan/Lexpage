from settings_common import *
import os

# General
DEBUG = True
SECRET_KEY = 'SecretKeyForDevelopmentEnvironment'


# Configuration
WSGI_APPLICATION = 'ws4redis.django_runserver.application' # Needed for builtin runserver


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db'),
    }
}


# Email & admin
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin.dev@fakemail.com'
ADMINS = (
    ('AdminDev', 'admin.dev@fakemail.com'),
)
MANAGERS = ADMINS


# Recaptcha
RECAPTCHA_PRIVATE_KEY = None
NOCAPTCHA = False  # Input field, enter "PASSED" in the captcha field to bypass captcha while testing.
os.environ['RECAPTCHA_TESTING'] = 'True'


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Websockets
REDIS_PUBLISHER = 'redis_helpers.FakeRedisPublisher'
WS4REDIS_SUBSCRIBER = 'redis_helpers.FakeRedisSubscriber'


# Tests
SELENIUM_WEBDRIVER = os.environ.get('SELENIUM_WEBDRIVER', None)
START_REDIS_COMMAND = os.environ.get('START_REDIS_COMMAND', None)
STOP_REDIS_COMMAND = os.environ.get('STOP_REDIS_COMMAND', None)
