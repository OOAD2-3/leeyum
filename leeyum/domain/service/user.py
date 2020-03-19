from django.db.models import Q, F

from leeyum.domain.models import ArticleStore, UserStore
from leeyum.domain.service.async_job import record_article_click_times
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
        # 【check】 service返回的尽可能是对象 而不是dict
        articles = ArticleStore.objects.filter(Q(publisher_id=publisher.id) & Q(status=0))
        for article in articles:
            article.concrete_article()

        return articles

    def add_like_article(self, user, article_id, *args, **kwargs):
        """
        添加收藏
        """
        article = get_object_or_404(ArticleStore, id=article_id)
        user.like_article.add(article)

        return article

    def delete_like_article(self, user, article_id, *args, **kwargs):
        """
        取消收藏
        """
        article = get_object_or_404(ArticleStore, id=article_id)
        user.like_article.remove(article)

        return True

    def list_like_article(self, user, *args, **kwargs):
        """
        获取用户收藏记录
        """
        articles = user.like_article.all().order_by('-id')
        for article in articles:
            article.concrete_article()

        return articles

    def is_liked(self, user, article, *args, **kwargs):
        """
        文章是否被当前用户收藏
        """
        if not user:
            return False
        return article.id in (article.id for article in user.like_article.all())

    def get_liked_times_by_article(self, article, *args, **kwargs):
        """
        获取article被收藏次数
        """
        # 【check】尽可能减少查库次数
        return article.userstore_set.all().count()

    def get_liked_times_by_user(self, user, *args, **kwargs):
        """
        获取用户被收藏总次数
        """
        published_articles = self.list_published_article(publisher=user)
        liked_times = 0
        for article in published_articles:
            liked_times += self.get_liked_times_by_article(article=article)

        return liked_times

    def add_viewed_article(self, user, article_id, *args, **kwargs):
        if user:
            # 埋点记录
            record_article_click_times.delay(article_id=article_id, user_id=user.id)
            # redis记录
            REDIS_CLIENT.put_history(name=user.id, value=article_id)
        ArticleStore.objects.filter(id=article_id).update(viewed_times=F('viewed_times')+1)

        return True

    def list_viewed_article(self, user, *args, **kwargs):
        # 浏览记录为30条
        viewed_articles = []
        viewed_article_id = REDIS_CLIENT.get_history(name=user.id)
        for article_id in viewed_article_id:
            article = ArticleStore.objects.filter(id=article_id).first()
            if article:
                article.concrete_article()
                viewed_articles.append(article)

        return viewed_articles

    def clear_viewed_article(self, user, *args, **kwargs):
        # 清除浏览记录
        if user:
            REDIS_CLIENT.clear_history(name=user.id)

        return True

USER_SERVICE = UserService()
