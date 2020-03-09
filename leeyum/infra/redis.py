from django.core.cache import cache
from django_redis import get_redis_connection
from redis import StrictRedis
from sensitive_settings import *

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

    def put_history(self, name, value):
        """
        默认历史浏览记录为30条
        """
        try:
            con = StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            history_key = 'history_%d' % name
            pl = con.pipeline()
            pl.lrem(history_key, 0, value)
            pl.lpush(history_key, value)
            pl.ltrim(history_key, 0, 29)
            pl.execute()
            print(value)
        except Exception as e:
            raise RedisContactException(e, message='redis访问出问题')

    def get_history(self, name):
        try:
            con = StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            history_key = 'history_%d' % name
            return con.lrange(history_key, 0, -1)
        except Exception as e:
            raise RedisContactException(e, message='redis访问出问题')


REDIS_CLIENT = RedisClient()
