from settings_dev import *


# Static
MINIFY_JS = MINIFY_CSS = True


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.path.join(BASE_DIR, 'db'),
        'USER': 'postgres',
    }
}


# Websockets
REDIS_PUBLISHER = None
WS4REDIS_SUBSCRIBER = 'ws4redis.subscriber.RedisSubscriber'

