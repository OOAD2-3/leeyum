# 参考文档：https://www.django-rest-framework.org/tutorial/1-serialization/
from django.core.mail import send_mail, EmailMessage
from django.template import loader
from rest_framework.exceptions import ParseError

from django.contrib.auth import login, authenticate, logout
from rest_framework.permissions import IsAuthenticated

from leeyum.domain.models import UserStore, ArticleStore

from leeyum.domain.service.user import USER_SERVICE
from leeyum.resource.exception import LoginException
from leeyum.views import BaseViewSet, BaseSerializer
from leeyum.views import JSONResponse
from mysite.settings import EMAIL_HOST_USER


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
            username = 'LEEYUM_uID_' + ''.join(phone_number[-4::])
            profile_avatar_url = 'https://leeyum-bucket.oss-cn-hangzhou.aliyuncs.com/default_front_file/%E7%94%A8%E6%88%B7%E5%A4%B4%E5%83%8F.jpg'
            UserStore.objects.create_user(username=username, phone_number=phone_number, profile_avatar_url=profile_avatar_url)

        user = authenticate(phone_number=phone_number, captcha=captcha)
        if user:
            login(request, user)
            return JSONResponse(code=200,
                                data={
                                    'username': user.username
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
        return JSONResponse(data=now_user.to_normal_dict())

    def add_like_article(self, request):
        """
        添加收藏
        """
        user = request.user
        article_id = request.json_data.get('article_id')
        article = USER_SERVICE.add_like_article(user=user, article_id=article_id)
        return JSONResponse(data=article.to_dict(fields=('id', 'title', 'pic_urls')))

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

        like_article_list = []
        articles = USER_SERVICE.list_like_article(user=user)
        for article in articles:
            if not article.is_take_off():
                article.concrete_article()
                like_article_list.append(article.to_dict(exclude=('publisher', 'report_level')))
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

        published_article_list = []
        articles = USER_SERVICE.list_published_article(publisher=user)
        for article in articles:
            if not article.is_take_off():
                article.concrete_article()
                published_article_list.append(article.to_dict(exclude=('publisher', 'report_level')))
        published_article_list.reverse()
        return JSONResponse(data=published_article_list)

    def list_viewed_article(self, request):
        """
        获取浏览记录
        """
        user = request.user

        viewed_article_list = []
        viewed_articles = USER_SERVICE.list_viewed_article(user=user)
        for article in viewed_articles:
            if article['status'] != ArticleStore.DELETE_STATUS:
                viewed_article_list.append(article)
        return JSONResponse(data=viewed_article_list)

    def list_teams(self, request):
        """
        获取组队记录
        """
        teams = request.user.teams.all()
        res = []
        for item in teams:
            if not item.is_take_off():
                item.concrete_article()
                res.append(item.to_dict(exclude=('publisher', 'report_level')))

        return JSONResponse(data=res)

    def student_authentication(self, request):
        """
        学生认证
        """
        html_message = """
        <div bgcolor="#17212e">
            <span style="font-size: 24px; color: #66c0f4; font-family: Arial, Helvetica, sans-serif; font-weight: bold;"> 
                {code} 
            </span>
        <div>
        """

        res = send_mail(subject='流云学生认证',
                        message='尊敬的流云用户13063031520：\n您的验证码为 ',
                        from_email=EMAIL_HOST_USER,
                        recipient_list=['24320162202918@stu.xmu.edu.cn'],
                        html_message='<div><span style="font-size: 24px; color: #66c0f4; font-family: Arial, Helvetica, sans-serif; font-weight: bold;"> {code} </span><div>')
        return JSONResponse(data="发送成功") if res == 1 else JSONResponse(data="发送失败")

    def update(self, request):
        """
        修改用户信息
        用户设置
        开关设置
        """
        now_user = request.user
        username = request.json_data.get('username')
        profile_avatar_url = request.json_data.get('profile_avatar_url')
        accept_recommended_message = request.json_data.get('accept_recommended_message')
        accept_publish_article_recommend_to_others = request.json_data.get('accept_publish_article_recommend_to_others')
        update_user = USER_SERVICE.update(user=now_user, username=username,
                                          profile_avatar_url=profile_avatar_url,
                                          accept_recommended_message=accept_recommended_message,
                                          accept_publish_article_recommend_to_others=accept_publish_article_recommend_to_others)
        return JSONResponse(data=update_user.to_normal_dict())

    def clear_viewed_article(self, request):
        """
        清除浏览记录
        """
        user = request.user
        USER_SERVICE.clear_viewed_article(user=user)
        return JSONResponse(message='clear viewed article success')
