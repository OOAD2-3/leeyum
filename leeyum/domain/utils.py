import re
import random
import hashlib
import time

from django.forms import model_to_dict

from leeyum.domain.models import BaseModel
from leeyum.resource import exception


def validate_phone_number(phone_number):
    """
    验证手机号是否合法
    """
    if not re.match(r"^1[35678]\d{9}$", phone_number):
        raise exception.PhoneNumberWrongException('number({}) is illegal'.format(phone_number))


def captcha_generator(number):
    """
    验证码生成器
    """
    result = ''
    for i in range(number):
        index = random.randrange(0, 2)
        if index == 0:
            result += chr(random.randint(65, 90))
        else:
            result += str(random.randint(1, 9))
    return result


def model_2_dict(model):
    result = model_to_dict(model)

    def _check(item):
        if type(item) is dict:
            for key, value in item.items():
                item[key] = _check(value)
            return item
        elif type(item) is list:
            return [_check(obj) for obj in item]
        elif isinstance(item, BaseModel):
            return model_2_dict(item)
        else:
            return item

    return _check(result)


def to_sha1_string(string):
    now = time.time()
    string += str(now)

    sha = hashlib.sha1(string.encode('utf-8'))
    encrypts = sha.hexdigest()
    return encrypts
