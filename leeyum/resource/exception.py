import six
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException

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


def custom_exception_handler(exc, context):
    """
    DRF 统一异常处理函数
    """
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

    if isinstance(exc, Exception):
        return ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(exc))
