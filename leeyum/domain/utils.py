import re
import random
import hashlib
import time
from datetime import datetime

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


def to_sha1_string(string):
    now = time.time()
    string += str(now)

    sha = hashlib.sha1(string.encode('utf-8'))
    encrypts = sha.hexdigest()
    return encrypts


def datetime_to_utc(_datetime):
    return _datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")


def utc_to_datetime(utc_string):
    return datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%S.%f")
