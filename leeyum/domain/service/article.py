__all__ = ('ARTICLE_SERVICE',)

from rest_framework.exceptions import ValidationError

from leeyum.domain.models import ArticleStore


class ArticleService(object):
    """
    信息
    """
    def create(self, title, pics, content, *args, **kwargs):
        """
        新建
        """
        tags_id = kwargs.get('tags_id', [])
        category_id = kwargs.get('category_id')

        if not category_id or type(category_id) is not int:
            raise ValidationError('新建article失败, 参数category_id格式错误 category_id = {}'.format(category_id))

        try:
            create_article = ArticleStore(title=title, pic_urls='["http://www.baidu.com"]', content=content)
            create_article.tags.add(*tags_id)
            create_article.category_id = category_id
            create_article.save()
            return create_article
        except Exception as e:
            raise e


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
