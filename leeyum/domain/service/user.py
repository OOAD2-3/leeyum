from random import random

from leeyum.domain.utils import captcha_generator, validate_phone_number
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

    def generate_captcha(self, phone_number):
        """
        生成验证码并发送
        """
        validate_phone_number(phone_number)

        # 验证码过期时间 10分钟
        captcha_expired_time = 60*10
        # 验证码位数
        captcha_number = 4

        captcha_code = captcha_generator(captcha_number)
        REDIS_CLIENT.put_object(phone_number, captcha_code, captcha_expired_time)
        ALI_SMS.send_sms(phone_number, captcha_code)
        return captcha_code


USER_SERVICE = UserService()
