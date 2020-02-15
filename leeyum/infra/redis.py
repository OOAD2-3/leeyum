from django.core.cache import cache

__all__ = ('REDIS_CLIENT',)


class RedisClient(object):

    def put_object(self, name, obj, expired_time):
        # TODO 加入异常处理
        cache.set(name, obj, expired_time)

    def get_object(self, name):
        return cache.get(name)


REDIS_CLIENT = RedisClient()
