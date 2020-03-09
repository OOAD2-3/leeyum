from traceback import print_exc

import six
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException

from leeyum.views import ErrorResponse


class BusinessException(Exception):
    business_code = 400
    business_message = 'Error occur'

    def __init__(self, *args, **kwargs):
        message = kwargs.get('message')
        if message:
            del kwargs['message']
            self.business_message = self.business_message + ': ' + message

        Exception.__init__(self, self.business_message, args, kwargs)


class PhoneNumberWrongException(BusinessException):
    business_code = 400
    business_message = 'Phone number wrong'


class RedisContactException(BusinessException):
    business_code = 500
    business_message = 'Redis Error occur'


class FileTypeException(BusinessException):
    business_code = 400
    business_message = 'File Type Wrong'


class FileTooBigException(BusinessException):
    business_code = 400
    business_message = 'File Too Big'


class LoginException(BusinessException):
    business_code = 400
    business_message = 'Login Fail'


class ActionRecordException(BusinessException):
    business_code = 400
    business_message = 'action record fail'


class JoinTeamException(BusinessException):
    business_code = 400
    business_message = 'join(leave) team fail'


def custom_exception_handler(exc, context):
    """
    DRF 统一异常处理函数
    """
    # 打印异常至控制台 方便排查问题
    print_exc()

    if isinstance(exc, BusinessException):
        return ErrorResponse(status=exc.business_code, message=exc.business_message)

    if isinstance(exc, APIException):
        msg = exc.default_detail
        data = {
            'detail': six.text_type(msg)
        }
        exc_message = str(exc)
        if 'CSRF' in exc_message:
            data['detail'] = exc_message

        return ErrorResponse(data, message=exc.detail, status=exc.status_code)

    if isinstance(exc, Http404):
        return ErrorResponse(status=status.HTTP_404_NOT_FOUND, message=str(exc))

    if isinstance(exc, Exception):
        return ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(exc))
