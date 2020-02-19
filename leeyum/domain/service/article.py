__all__ = ('ARTICLE_SERVICE',)

import json

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from leeyum.domain.models import ArticleStore, FileUploadRecorder
from leeyum.domain.utils import to_sha1_string
from leeyum.infra.aliCloud import ALI_STORAGE
from leeyum.resource.exception import FileTypeException, FileTooBigException


class ArticleService(object):
    """
    信息
    """
    def get_details(self, article_id):
        article = get_object_or_404(ArticleStore, id=article_id)

        article.pic_urls = json.loads(article.pic_urls)
        article.content = json.loads(article.content)
        return article

    def create(self, title, pic_urls, content, creator, *args, **kwargs):
        """
        新建
        """
        tags_id = kwargs.get('tags_id', [])
        category_id = kwargs.get('category_id')

        if not category_id or type(category_id) is not int:
            raise ValidationError('新建article失败, 参数category_id格式错误 category_id = {}'.format(category_id))

        try:
            content = ArticleStore.format_content(body=content)
            create_article = ArticleStore(title=title, pic_urls=json.dumps(pic_urls), content=content)
            if tags_id:
                create_article.tags.add(*tags_id)
            create_article.publisher_id = creator.id
            create_article.category_id = category_id
            create_article.save()

            # 同步至es中
            ARTICLE_INDEX_SERVICE.publish(create_article)
            return create_article
        except Exception as e:
            raise e

    def update(self, article_id, *args, **kwargs):
        update_article = get_object_or_404(ArticleStore, id=article_id)

        fields = ['title', 'content', 'pic_urls', 'tags_id', 'category_id']
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
                if f == 'tags_id':
                    update_article.tags.add(*value)
                    continue

                setattr(update_article, f, value)

        update_article.save()
        return update_article, update_fields

    def upload_pic(self, pic_file, uploader):
        # 限制大小 限制类型
        restricted_type = ('image/png', 'image/jpg', 'image/jpeg')
        max_size = 1024*1024*10
        if pic_file.content_type not in restricted_type:
            raise FileTypeException('file name: {}'.format(pic_file.name))
        if pic_file.size > max_size:
            raise FileTooBigException('file name: {}'.format(pic_file.name))

        ali_result = ALI_STORAGE.upload(file_name=pic_file.name, file=pic_file, prefix=uploader.username)
        pic_url = ali_result.resp.response.url

        file_upload_recorder, create = FileUploadRecorder \
            .objects.update_or_create(file_url=pic_url, defaults={'file_name': pic_file.name, 'is_used': False})

        return file_upload_recorder

    def diff_pic(self, article, pic_urls):
        """
        修改文件使用记录
        """
        db_pic_urls = json.loads(article.pic_urls)

        deleted_pic_urls = [item for item in db_pic_urls if item not in pic_urls]
        add_pic_urls = [item for item in pic_urls if item not in db_pic_urls]

        FileUploadRecorder.abandon_these_files(deleted_pic_urls)
        FileUploadRecorder.use_these_files(add_pic_urls)


class ArticleIndexService(object):
    """
    信息es存储
    """

    def init_model(self, model):
        pass

    def publish(self, article):
        pass

    def delete(self, article):
        pass

    def update(self, article):
        pass


ARTICLE_SERVICE = ArticleService()
ARTICLE_INDEX_SERVICE = ArticleIndexService()
