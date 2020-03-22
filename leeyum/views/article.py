import json

from django.core.paginator import Paginator
from rest_framework.exceptions import ValidationError, NotAuthenticated

from leeyum.domain.models import ArticleStore
from leeyum.domain.service.action import ACTION_SERVICE
from leeyum.domain.service.article import ARTICLE_SERVICE, ARTICLE_INDEX_SERVICE
from leeyum.domain.service.async_job import record_search_word
from leeyum.domain.service.user import USER_SERVICE
from leeyum.domain.utils import ShowType
from leeyum.infra.redis import REDIS_CLIENT
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class ArticleSerializer(BaseSerializer):
    class META:
        model = ArticleStore
        fields = ('__all__',)


class ArticleViewSet(BaseViewSet):

    def create(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")

        title = request.json_data.get('title')
        pic_urls = request.json_data.get('pic_urls', [])
        content_details = request.json_data.get('content', {})
        # 版本兼容处理
        if type(content_details) is str:
            content_details = {'body': content_details}

        tags = request.json_data.get('tags', [])
        category_id = request.json_data.get('category_id')

        article = ARTICLE_SERVICE \
            .create(title=title, pic_urls=pic_urls, content_details=content_details, creator=request.user, tags=tags,
                    category_id=category_id)

        return JSONResponse(data={'article_id': article.id})

    def update(self, request):
        article_id = request.json_data.get('id')
        title = request.json_data.get('title')
        pic_urls = request.json_data.get('pic_urls', [])
        content = request.json_data.get('content')
        tags = request.json_data.get('tags', [])
        category_id = request.json_data.get('category_id')

        article, update_fields = ARTICLE_SERVICE.update(article_id=article_id, title=title, pic_urls=pic_urls,
                                                        content=content, tags=tags, category_id=category_id)

        return JSONResponse(data={'article_id': article.id, 'update_fields': update_fields})

    def retrieve(self, request):
        reader = request.user if bool(request.user and request.user.is_authenticated) else None
        article_id = request.GET.get('id')
        article = ARTICLE_SERVICE.get_details(article_id)

        # 添加浏览记录
        USER_SERVICE.add_viewed_article(user=reader, article_id=article.id)
        dict_res = article.to_dict(exclude=('publisher', 'gmt_modified', 'gmt_created', 'viewed_times'))
        # 发布者信息
        publisher = article.publisher.to_dict(fields=('username', 'phone_number'))
        dict_res['publisher'] = publisher
        # view_times可能为null
        dict_res['viewed_times'] = article.viewed_times if article.viewed_times else 0
        # 被收藏次数
        dict_res['liked_times'] = USER_SERVICE.get_liked_times_by_article(article=article)
        # 是否被收藏
        dict_res['is_liked'] = USER_SERVICE.is_liked(reader, article)
        # 组队信息 - 是否加入组队
        if article.is_team_type() and reader:
            dict_res['team_has_joined'] = ARTICLE_SERVICE.is_inside_team(article, reader)

        return JSONResponse(data=dict_res)

    def list(self, request):
        """
        搜索 + 全量
        """
        reader = request.user if bool(request.user and request.user.is_authenticated) else None

        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        category = request.GET.get('category')
        if category:
            category = int(category)

        # tags 参数使用,分割符传递
        tags = request.GET.get('tags', '')
        if tags:
            tags = tags.split(',')

        is_main = request.GET.get('is_main')
        if is_main is not None:
            article_list = ARTICLE_SERVICE.show(show_type=ShowType.monthly_hot, category=category, tags=tags)
        else:
            keyword = request.GET.get('keyword')
            article_list = ARTICLE_INDEX_SERVICE.search(keyword=keyword)
            if reader:
                record_search_word.delay(keyword=keyword, user_id=reader.id)

        paginator = Paginator(article_list, page_size)
        page_info = paginator.page(page)

        return JSONResponse({"article_list": page_info.object_list, "has_next_page": page_info.has_next(),
                             "page": page, "page_size": paginator.per_page, "total": paginator.count})

    def take_off(self, request):
        """
        下架
        """
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")
        article_id = request.GET.get('id')
        ARTICLE_SERVICE.delete(article_id=article_id)
        return JSONResponse(message="下架成功")

    def upload_file(self, request):
        request_file = request.FILES.get('file')
        if not request_file:
            raise ValidationError('cannot get any files')

        file_upload_recorder = ARTICLE_SERVICE.upload_pic(pic_file=request_file, uploader=request.user)
        return JSONResponse(data=file_upload_recorder.to_dict())

    def join_team(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")

        article_id = request.json_data.get('article_id')
        res = ARTICLE_SERVICE.join_team(article_id=article_id, user=request.user)
        return JSONResponse(res.concrete_article().to_dict(exclude=('publisher',)))

    def leave_team(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")

        article_id = request.json_data.get('article_id')
        res = ARTICLE_SERVICE.leave_team(article_id=article_id, user=request.user)
        return JSONResponse(res.concrete_article().to_dict(exclude=('publisher',)))


class ArticleRelationViewSet(BaseViewSet):
    """
    article相关的周边接口
    """
    def get_hot_word(self, request):
        number = request.GET.get('number', 10)
        hot_words = REDIS_CLIENT.get_object('ACTION_SERVICE.retrieve_hot_word(number={})'.format(number))
        if not hot_words:
            hot_words = ACTION_SERVICE.retrieve_hot_word(number=number)
            REDIS_CLIENT.put_object('ACTION_SERVICE.retrieve_hot_word(number={})'.format(number), hot_words)

        return JSONResponse(hot_words)

