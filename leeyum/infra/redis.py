from django.core.cache import cache

__all__ = ('REDIS_CLIENT',)

from leeyum.resource.exception import RedisContactException


class RedisClient(object):
    cache_prefix = 'leeyum.cache.{}'

    def put_object(self, name, obj, expired_time=60 * 10):
        """
        默认过期时间10分钟
        """
        try:
            cache.set(self.cache_prefix.format(name), obj, expired_time)
        except Exception as e:
            raise RedisContactException(e, message='redis访问出问题')

    def get_object(self, name):
        try:
            return cache.get(self.cache_prefix.format(name))
        except Exception as e:
            raise RedisContactException(e, message='redis访问出问题')


REDIS_CLIENT = RedisClient()
