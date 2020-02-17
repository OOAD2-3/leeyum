# 参考文档：https://www.django-rest-framework.org/tutorial/1-serialization/
from rest_framework.exceptions import ParseError

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from leeyum.domain.models import UserStore

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

    def login(self, request):
        phone_number = request.POST.get('phone_number')
        captcha = request.POST.get('captcha')
        if UserStore.objects.filter(phone_number=phone_number):
            user = authenticate(phone_number=phone_number, captcha=captcha)
            if user:
                login(request, user)
                return JSONResponse(code=200,
                                    data={
                                        'phone_number': user.phone_number
                                    },
                                    message='登录成功')
            else:
                return JSONResponse(message='登录失败')
        else:
            UserStore.objects.create_user(username=phone_number, phone_number=phone_number)
            user = authenticate(phone_number=phone_number, captcha=captcha)
            if user:
                login(request, user)
                return JSONResponse(code=200,
                                    data={
                                        'phone_number': user.phone_number
                                    },
                                    message='第一次登录成功')
            else:
                return JSONResponse(message='第一次登录失败')

    @login_required
    def logout(self, request):
        logout(request)
        return JSONResponse(message='登出成功')
