from django.core.paginator import Paginator
from rest_framework.exceptions import ValidationError, NotAuthenticated

from leeyum.domain.models import ArticleStore
from leeyum.domain.service.article import ARTICLE_SERVICE, ARTICLE_INDEX_SERVICE
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
        content = request.json_data.get('content')
        tags = request.json_data.get('tags', [])
        category_id = request.json_data.get('category_id')

        article = ARTICLE_SERVICE \
            .create(title=title, pic_urls=pic_urls, content_body=content, creator=request.user, tags=tags,
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
        article_id = request.GET.get('id')
        res = ARTICLE_SERVICE.get_details(article_id)

        dict_res = res.to_dict(exclude=('publisher', 'gmt_modified', 'gmt_created'))
        publisher = res.publisher.to_dict(fields=('username',))
        dict_res['publisher'] = publisher
        return JSONResponse(data=dict_res)

    def list(self, request):
        """
        搜索 + 全量
        """
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
            article_list = ARTICLE_SERVICE.show(category=category, tags=tags)
        else:
            keyword = request.GET.get('keyword')
            article_list = ARTICLE_INDEX_SERVICE.search(keyword=keyword, category=category, tags=tags)

        paginator = Paginator(article_list, page_size)
        page_info = paginator.page(page)

        return JSONResponse({"article_list": page_info.object_list, "has_next_page": page_info.has_next(), "page": paginator.num_pages,
                             "page_size": paginator.per_page, "total": paginator.count})

    def upload_file(self, request):
        request_file = request.FILES.get('file')
        if not request_file:
            raise ValidationError('cannot get any files')

        file_upload_recorder = ARTICLE_SERVICE.upload_pic(pic_file=request_file, uploader=request.user)
        return JSONResponse(data=file_upload_recorder.to_dict())
