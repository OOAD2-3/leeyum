from django.http import HttpResponse

from leeyum.domain.service.article import ARTICLE_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class ArticleSerializer(BaseSerializer):
    pass


class ArticleViewSet(BaseViewSet):

    def create(self, request):
        title = request.json_data.get('title')
        content = request.json_data.get('content')
        tags_id = request.json_data.get('tags_id', [])
        category_id = request.json_data.get('category_id')

        # 图片文件
        pic_files = None

        article = ARTICLE_SERVICE\
            .create(title=title, pics=pic_files, content=content, tags_id=tags_id, category_id=category_id)

        return JSONResponse(data={'article_id': article.id})

    def update(self, request):
        pass

    def retrieve(self, request):
        return HttpResponse('123')

    def list(self, request):
        """
        搜索 + 全量
        """
        return HttpResponse('123')
