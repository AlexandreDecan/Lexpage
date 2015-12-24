from django.conf import settings
from django.utils.module_loading import import_string
from ws4redis.publisher import RedisPublisher
from ws4redis.subscriber import RedisSubscriber
from ws4redis.redis_store import RedisStore
try:
    import redislite
    # We instantiate here so it is shared everywhere.
    # If we instantiate in the subclasses they use "different redis servers".
    r = redislite.StrictRedis()
except ImportError:
    # redislite is not installed, let's assume we won't need it.
    pass


def get_redis_publisher():
    if hasattr(settings, 'REDIS_PUBLISHER'):
        redis_publisher_path = getattr(settings, 'REDIS_PUBLISHER')
    else:
        redis_publisher_path = None
    if redis_publisher_path is None:
        return RedisPublisher
    return import_string(redis_publisher_path)


class FakeRedisSubscriber(RedisSubscriber):
    def __init__(self, connection):
        #self._subscription = self._connection.pubsub()
        return super(RedisSubscriber, self).__init__(r)
#    def get_file_descriptor(self):
#        return None

class FakeRedisPublisher(RedisPublisher):
    def __init__(self, **kwargs):
        connection = r
        RedisStore.__init__(self, connection)
        for key in self._get_message_channels(**kwargs):
            self._publishers.add(key)



