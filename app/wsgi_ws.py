import os
import gevent.socket
import gevent.monkey
import redis.connection

gevent.monkey.patch_thread()
redis.connection.socket = gevent.socket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from ws4redis.uwsgi_runserver import uWSGIWebsocketServer

application = uWSGIWebsocketServer()


