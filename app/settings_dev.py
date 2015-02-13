#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

import os

from settings_base import *


SECRET_KEY = 'SecretKeyForDevelopmentEnvironment'
RECAPTCHA_PUBLIC_KEY = None
RECAPTCHA_PRIVATE_KEY = None

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_MAIL = 'no-reply@lexpage.net'



ADMINS = (
    ('AdminDev', 'admin.dev@fakemail.com'),
)
MANAGERS = ADMINS


DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ['127.0.0.1',]



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(BASE_DIR, 'db'),                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}


LOGGING = None
