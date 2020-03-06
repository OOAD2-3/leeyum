from leeyum.domain.models import ArticleStore, UserStore
from leeyum.domain.utils import captcha_generator, validate_phone_number
from django.shortcuts import get_object_or_404

from leeyum.infra.aliCloud import ALI_SMS
from leeyum.infra.redis import REDIS_CLIENT

__all__ = ('USER_SERVICE',)


class UserService(object):
    """
    用户
    """
    def login(self, phone_number, captcha):
        pass

    def logout(self):
        pass

    def generate_captcha(self, phone_number):
        """
        生成验证码并发送
        """
        validate_phone_number(phone_number)

        # 验证码过期时间 10分钟
        captcha_expired_time = 60*10
        # 验证码位数
        captcha_number = 4

        captcha_code = captcha_generator(captcha_number)
        REDIS_CLIENT.put_object(phone_number, captcha_code, captcha_expired_time)
        ALI_SMS.send_sms(phone_number, captcha_code)
        return captcha_code

    def update(self, user, *args, **kwargs):
        """
        修改用户信息
        """
        fields = ['username', 'profile_avatar_url']
        update_fields = []

        for f in fields:
            if kwargs.get(f):
                update_fields.append(f)
                value = kwargs.get(f)

                setattr(user, f, value)
        user.save()
        return user

    def list_published_article(self, publisher, *args, **kwargs):
        """
        获取用户发布记录
        """
        published_article_list = []
        published_articles = ArticleStore.objects.filter(publisher_id=publisher.id)
        for article in published_articles:
            published_article_list.append(article.id)
        return published_article_list

    def add_like_article(self, user, article_id, *args, **kwargs):
        """
        添加收藏
        """
        article = get_object_or_404(ArticleStore, id=article_id)
        user.like_article.add(article)
        like_article_list = self.list_like_article(user=user)
        return like_article_list

    def delete_like_article(self, user, article_id, *args, **kwargs):
        """
        取消收藏
        """
        article = get_object_or_404(ArticleStore, id=article_id)
        user.like_article.remove(article)
        like_article_list = self.list_like_article(user=user)
        return like_article_list

    def list_like_article(self, user, *args, **kwargs):
        """
        获取用户收藏记录
        """
        like_article_list = []
        articles = user.like_article.all()
        for article in articles:
            like_article_list.append(article.id)
        return like_article_list

    def get_liked_times_by_article(self, article_id, *args, **kwargs):
        """
        获取article被收藏次数
        """
        article = get_object_or_404(ArticleStore, id=article_id)
        liked_times = article.userstore_set.all().count()
        return liked_times

    def get_liked_times_by_user(self, user, *args, **kwargs):
        """
        获取user下的article被收藏总次数
        """
        articles = self.list_published_article(publisher=user)
        like_times = 0
        for article in articles:
            like_times = like_times + self.get_liked_times_by_article(article_id=article.id)
        return like_times


USER_SERVICE = UserService()
