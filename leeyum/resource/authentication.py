from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from leeyum.domain.models import UserStore
from leeyum.domain.service.user import USER_SERVICE


class CaptchaModelBackend(ModelBackend):
    """
    继承ModelBackend类，重写authenticate()方法
    自定义用户验证后端：支持用户名或邮箱登录。
    """
    def authenticate(self, request, username=None, captcha=None, phone_number=None, **kwargs):
        try:
            if captcha is None or phone_number is None:
                return None

            user = UserStore.objects.get(Q(phone_number=phone_number) | Q(username=username))
            if user.check_captcha(phone_number, captcha):
                return user

        except Exception as e:
            return None


class PasswordModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserStore.objects.get(username=username)
            if user.check_password(password):
                return user

        except Exception as e:
            raise PermissionDenied(e)
