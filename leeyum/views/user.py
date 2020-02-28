# 参考文档：https://www.django-rest-framework.org/tutorial/1-serialization/
from rest_framework.exceptions import ParseError

from django.contrib.auth import login, authenticate, logout
from rest_framework.permissions import IsAuthenticated

from leeyum.domain.models import UserStore

from leeyum.domain.service.user import USER_SERVICE
from leeyum.resource.exception import LoginException
from leeyum.views import BaseViewSet, BaseSerializer
from leeyum.views import JSONResponse


class UserSerializer(BaseSerializer):
    pass


class UserCommonViewSet(BaseViewSet):

    def get_captcha(self, request):
        """
        获取验证码
        """
        phone_number = request.GET.get('phone_number')
        if not phone_number:
            raise ParseError('phone_number does not exist')
        USER_SERVICE.generate_captcha(str(phone_number))
        return JSONResponse({'phone_number': phone_number}, message='验证码短信发送成功')

    def login(self, request):
        """
        登录&注册
        """
        phone_number = request.POST.get('phone_number')
        captcha = request.POST.get('captcha')

        if not UserStore.objects.filter(phone_number=phone_number):
            UserStore.objects.create_user(username=phone_number, phone_number=phone_number)

        user = authenticate(phone_number=phone_number, captcha=captcha)
        if user:
            login(request, user)
            return JSONResponse(code=200,
                                data={
                                    'phone_number': user.phone_number
                                },
                                message='登录成功')
        else:
            raise LoginException(message='登陆失败, phone_number: {}, captcha: {}'.format(phone_number, captcha))


class UserViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]

    def logout(self, request):
        logout(request)
        return JSONResponse(message='登出成功')

    def retrieve(self, request):
        """
        获取用户信息
        """
        now_user = request.user
        return JSONResponse(data=now_user.to_dict(fields=('username', 'phone_number', 'profile_avatar_url')))
