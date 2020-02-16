# 参考文档：https://www.django-rest-framework.org/tutorial/1-serialization/
from leeyum.domain.service.user import USER_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer
from leeyum.views import JSONResponse


class UserSerializer(BaseSerializer):
    pass


class UserViewSet(BaseViewSet):
    def get_captcha(self, request):
        phone_number = request.GET.get('phone_number')
        res = USER_SERVICE.generate_captcha(phone_number)
        if res:
            return JSONResponse({'hello': '这是个实验'}, message='生成验证码成功')
        else:
            return JSONResponse(code=500, message='生成验证码失败')
