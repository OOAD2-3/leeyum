__all__ = ('ARTICLE_SERVICE', 'ARTICLE_INDEX_SERVICE')

import json

import requests
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from leeyum.domain.models import ArticleStore, FileUploadRecorder
from leeyum.domain.service.category import CATEGORY_SERVICE
from leeyum.domain.utils import utc_to_datetime
from leeyum.infra.aliCloud import ALI_STORAGE
from leeyum.resource.exception import FileTypeException, FileTooBigException


class ArticleService(object):
    """
    信息
    """

    def get_details(self, article_id):
        article = get_object_or_404(ArticleStore, id=article_id)

        article.concrete_article()
        return article

    def create(self, title, pic_urls, content_body, creator, *args, **kwargs):
        """
        新建
        """
        tags = kwargs.get('tags', [])
        category_id = kwargs.get('category_id')

        if not category_id or type(category_id) is not int:
            raise ValidationError('新建article失败, 参数category_id格式错误 category_id = {}'.format(category_id))

        try:
            content = ArticleStore.format_content(body=content_body)
            create_article = ArticleStore(title=title, pic_urls=json.dumps(pic_urls), content=content)
            if tags:
                create_article.tags = json.dumps(tags)
            create_article.publisher_id = creator.id if creator.id is not None else 1
            create_article.category_id = category_id
            create_article.status = ArticleStore.NORMAL_STATUS
            create_article.save()

            # 将文件置为已使用
            FileUploadRecorder.use_these_files(pic_urls)

            # 同步至es中
            ARTICLE_INDEX_SERVICE.publish(create_article)
            return create_article
        except Exception as e:
            raise e

    def update(self, article_id, *args, **kwargs):
        update_article = get_object_or_404(ArticleStore, id=article_id)
        update_article.concrete_article()

        fields = ['title', 'content', 'pic_urls', 'tags', 'category_id']
        update_fields = []

        for f in fields:
            if kwargs.get(f):
                update_fields.append(f)
                value = kwargs.get(f)
                if f == 'content':
                    value = ArticleStore.format_content(body=value)
                if f == 'pic_urls':
                    self.diff_pic(update_article, pic_urls=value)
                    value = json.dumps(value)
                if f == 'tags':
                    value = json.dumps(value)

                setattr(update_article, f, value)

        update_article.save()
        return update_article, update_fields

    def upload_pic(self, pic_file, uploader):
        # 限制大小 限制类型
        restricted_type = ('image/png', 'image/jpg', 'image/jpeg')
        max_size = 1024 * 1024 * 10
        if pic_file.content_type not in restricted_type:
            raise FileTypeException(message='file name: {}'.format(pic_file.name))
        if pic_file.size > max_size:
            raise FileTooBigException(message='file name: {}'.format(pic_file.name))

        ali_result = ALI_STORAGE.upload(file_name=pic_file.name, file=pic_file, uploader=uploader.username)
        pic_url = ali_result.resp.response.url

        file_upload_recorder, create = FileUploadRecorder \
            .objects.update_or_create(file_url=pic_url, defaults={'file_name': pic_file.name, 'is_used': False})

        return file_upload_recorder

    def diff_pic(self, article, pic_urls):
        """
        修改文件使用记录
        """

        deleted_pic_urls = [item for item in article.pic_urls if item not in pic_urls]
        add_pic_urls = [item for item in pic_urls if item not in article.pic_urls]

        FileUploadRecorder.abandon_these_files(deleted_pic_urls)
        FileUploadRecorder.use_these_files(add_pic_urls)

    def show(self, category, tags):
        """
        首页-兴趣推荐
        """
        q = Q()
        if category and category > 0:
            # category只能单选查询
            category_leaves = CATEGORY_SERVICE.get_leaves(category_id=category)
            q |= Q(category__in=category_leaves)
        if tags:
            # tag可以多选查询
            for tag in tags:
                q |= Q(tags__contains=tag)

        result = []
        for article in ArticleStore.objects.filter(q).exclude(status=ArticleStore.DELETE_STATUS):
            article.concrete_article()
            result.append(article.to_dict(exclude=('publisher',)))

        return result


class ArticleIndexService(object):
    """
    elastic search
    """

    doc_url = 'http://120.26.88.97:9200/article/_doc/{doc_id}'
    search_url = 'http://120.26.88.97:9200/article/_search'

    def _write(self, article_id, data):
        if type(data) is not str:
            data = json.dumps(data)
        return requests.put(self.doc_url.format(doc_id=article_id), data=data,
                            headers={'Content-Type': 'application/json'})

    def _read(self, data):
        return requests.get(self.search_url, data=data, headers={'Content-Type': 'application/json'})

    def _delete(self, article_id):
        return requests.delete(self.doc_url.format(doc_id=article_id))

    def publish(self, article):
        data = article.generate_es_put_data()
        res = self._write(article.id, data)

        # 错误处理
        if int(res.status_code/100) != 2:
            article.status = ArticleStore.ES_ERROR_STATUS
            article.save()

        return res

    def delete(self, article_id):
        self._delete(article_id)

    def update(self, article):
        pass

    def search(self, keyword, *args, **kwargs):
        category = kwargs.get('category')
        tags = kwargs.get('tags')

        # 请求es服务器
        search_dsl = self._get_search_dsl(keyword, category, tags)
        res = self._read(search_dsl)
        res = json.loads(res.text)

        res_data_list = res.get('hits', {}).get('hits', [])
        return [self.format(res_data) for res_data in res_data_list]

    @staticmethod
    def format(es_obj):
        obj_id = es_obj.get('_id')
        source = es_obj.get('_source', {})
        article = ArticleStore()
        article.id = obj_id
        article.title = source.get('title')
        article.content = source.get('content')
        article.pic_urls = source.get('pic_urls')
        article.tags = source.get('tags')
        article.publish_time = utc_to_datetime(source.get('publish_time'))
        article.publisher_id = source.get('publisher')
        article.category_id = source.get('category')

        return article.to_dict(exclude=('publisher',))

    @staticmethod
    def _get_search_dsl(keyword, category=None, tags=None):
        if type(keyword) is list or type(keyword) is tuple:
            keyword = ','.join(keyword)
        base_search_dsl = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "nested": {
                                            "path": "content",
                                            "query": {
                                                "match": {
                                                    "content.body": keyword
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "title": keyword
                                        }
                                    },
                                    {
                                        "match": {
                                            "tags.keyword": keyword
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "content.body": {},
                    "title": {},
                    "tags": {}
                },
                "pre_tags": "<123>",
                "post_tags": "</123>"
            }
        }

        if type(tags) is list or type(tags) is tuple:
            tags = ','.join(tags)

        if tags:
            tag_dsl_part = {
                "match": {
                    "tags": tags
                }
            }
            base_search_dsl['query']['bool']['must'].append(tag_dsl_part)

        if category:
            category_dsl_part = {
                "match": {
                    "category": category
                }
            }
            base_search_dsl['query']['bool']['must'].append(category_dsl_part)
        return json.dumps(base_search_dsl)

    def _backdoor_refresh_es_data(self):
        for article in ArticleStore.objects.filter(status=ArticleStore.NORMAL_STATUS):
            self.publish(article)


ARTICLE_SERVICE = ArticleService()
ARTICLE_INDEX_SERVICE = ArticleIndexService()
