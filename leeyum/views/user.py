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

    def update(self, request):
        """
        修改用户信息
        """
        now_user = request.user
        username = request.json_data.get('username')
        profile_avatar_url = request.json_data.get('profile_avatar_url')
        update_user = USER_SERVICE.update(user=now_user, username=username,
                                          profile_avatar_url=profile_avatar_url)
        return JSONResponse(data=update_user.to_dict(fields=('username', 'phone_number', 'profile_avatar_url')))

    def add_like_article(self, request):
        """
        添加收藏
        """
        user = request.user
        article_id = request.json_data.get('article_id')
        article = USER_SERVICE.add_like_article(user=user, article_id=article_id)
        return JSONResponse(data=article.to_dict(fields=('id', 'title')))

    def delete_like_article(self, request):
        """
        取消收藏
        """
        user = request.user
        article_id = request.GET.get('article_id')
        USER_SERVICE.delete_like_article(user=user, article_id=article_id)
        return JSONResponse(message="delete like article success")

    def list_like_article(self, request):
        """
        获取收藏记录
        """
        user = request.user
        like_article_list = USER_SERVICE.list_like_article(user=user)
        return JSONResponse(data=like_article_list)

    def get_liked_times(self, request):
        """
        获取用户被收藏总次数
        """
        user = request.user
        like_times = USER_SERVICE.get_liked_times_by_user(user=user)
        return JSONResponse(data={'liked_times': like_times})

    def list_published_article(self, request):
        """
        获取发布记录
        """
        user = request.user
        published_article_list = USER_SERVICE.list_published_article(publisher=user)
        return JSONResponse(data=published_article_list)

    def list_viewed_article(self, request):
        """
        获取浏览记录
        """
        user = request.user
        viewed_article_list = USER_SERVICE.list_viewed_article(user=user)
        return JSONResponse(data=viewed_article_list)
