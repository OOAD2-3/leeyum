import re

from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin


class CtxMiddleware(MiddlewareMixin):
    TRUST_URL = ['/admin/', '/api/user/captcha', '/api/user/login']

    def process_request(self, request):
        if self.is_permission_path(request.path):
            return

        # 不处于登录态的不给登录
        if not request.user.is_authenticated:
            raise PermissionDenied('your have no permission')

    def is_permission_path(self, path):
        for pattens in self.TRUST_URL:
            if re.match(pattens, path):
                return True
        return False
