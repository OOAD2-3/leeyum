import re
import random
import hashlib
import time

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
