from django.core.cache import cache

__all__ = ('REDIS_CLIENT',)


class RedisClient(object):
    cache_prefix = 'leeyum.cache.{}'

    def put_object(self, name, obj, expired_time=60 * 10):
        """
        默认过期时间10分钟
        """

        cache.set(self.cache_prefix.format(name), obj, expired_time)

    def get_object(self, name):
        return cache.get(self.cache_prefix.format(name))


REDIS_CLIENT = RedisClient()
