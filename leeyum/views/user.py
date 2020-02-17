# 参考文档：https://www.django-rest-framework.org/tutorial/1-serialization/
from rest_framework.exceptions import ParseError

from leeyum.domain.service.user import USER_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer
from leeyum.views import JSONResponse


class UserSerializer(BaseSerializer):
    pass


class UserCommonViewSet(BaseViewSet):
    # 无须登陆
    authentication_classes = []
    permission_classes = []

    def get_captcha(self, request):
        """
        获取验证码
        """
        phone_number = request.GET.get('phone_number')
        if not phone_number:
            raise ParseError('phone_number does not exist')
        res = USER_SERVICE.generate_captcha(str(phone_number))
        if res:
            return JSONResponse({'phone_number': phone_number}, message='验证码短信发送成功')
        else:
            return JSONResponse(code=500, message='验证码短信发送失败')

    def login(self, request):
        pass


class UserViewSet(BaseViewSet):
    def logout(self, request):
        pass
