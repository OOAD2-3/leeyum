from rest_framework.exceptions import ValidationError

from leeyum.domain.models import ArticleStore
from leeyum.domain.service.article import ARTICLE_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class ArticleSerializer(BaseSerializer):
    class META:
        model = ArticleStore
        fields = ('__all__',)


class ArticleViewSet(BaseViewSet):

    def create(self, request):
        title = request.json_data.get('title')
        pic_urls = request.json_data.get('pic_urls', [])
        content = request.json_data.get('content')
        tags_id = request.json_data.get('tags_id', [])
        category_id = request.json_data.get('category_id')

        article = ARTICLE_SERVICE \
            .create(title=title, pic_urls=pic_urls, content=content, creator=request.user, tags_id=tags_id,
                    category_id=category_id)

        return JSONResponse(data={'article_id': article.id})

    def update(self, request):
        article_id = request.json_data.get('id')
        title = request.json_data.get('title')
        pic_urls = request.json_data.get('pic_urls', [])
        content = request.json_data.get('content')
        tags_id = request.json_data.get('tags_id', [])
        category_id = request.json_data.get('category_id')

        article, update_fields = ARTICLE_SERVICE.update(article_id=article_id, title=title, pic_urls=pic_urls,
                                                        content=content, tags_id=tags_id, category_id=category_id)

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
        return JSONResponse('123')

    def upload_file(self, request):
        request_file = request.FILES.get('file')
        if not request_file:
            raise ValidationError('cannot get any files')

        file_upload_recorder = ARTICLE_SERVICE.upload_pic(pic_file=request_file, uploader=request.user)
        return JSONResponse(data=file_upload_recorder.to_dict())
