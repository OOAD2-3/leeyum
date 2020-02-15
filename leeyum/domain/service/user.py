from random import random

from leeyum.domain.utils import captcha_generator
from leeyum.infra.aliCloud import ALI_SMS
from leeyum.infra.redis import REDIS_CLIENT

__all__ = ('USER_SERVICE',)


class UserService(object):
    """
    用户
    """
    def login(self):
        pass

    def logout(self):
        pass

    def validate_captcha(self, phone_number, captcha):
        """
        验证传入短信验证码是否正确
        """
        redis_value = REDIS_CLIENT.get_object(phone_number)
        return redis_value == captcha

    def generate_captcha(self, phone_number):
        """
        生成验证码并发送
        TODO 发送短信还未完全可用
        """
        # 验证码过期时间 10分钟
        captcha_expired_time = 60*10
        # 验证码位数
        captcha_number = 4

        def put_in_redis(captcha):
            """
            存入redis
            """
            REDIS_CLIENT.put_object(phone_number, captcha, captcha_expired_time)

        captcha_code = captcha_generator(captcha_number)
        put_in_redis(captcha_code)
        # TODO 暂不可用 ALI_SMS.send_sms(phone_number, captcha_code)
        return captcha_code


USER_SERVICE = UserService()
