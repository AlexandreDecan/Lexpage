from settings_dev import *
import os

# General
DEBUG = False


# Websockets
REDIS_PUBLISHER = None
WS4REDIS_SUBSCRIBER = 'ws4redis.subscriber.RedisSubscriber'


# Selenium Webdriver
# Travis SHOULD add this environment variable
SELENIUM_WEBDRIVER = os.environ['SELENIUM_WEBDRIVER']


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.path.join(BASE_DIR, 'db'),
        'USER': 'postgres',
    }
}

