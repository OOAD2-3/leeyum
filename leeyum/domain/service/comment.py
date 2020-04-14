from django.db.models import Q

from rest_framework.exceptions import ValidationError, PermissionDenied
from leeyum.domain.models import CommentStore, UserStore
from django.shortcuts import get_object_or_404

from leeyum.infra.sensitiveFilter import SENSITIVE_FILTER

__all__ = ('COMMENT_SERVICE',)


class CommentService(object):
    """
    评论模块
    """

    def create(self, message, comment_article_id, comment_publisher, *args, **kwargs):
        """
        新建评论
        """
        if not comment_article_id or type(comment_article_id) is not int:
            raise ValidationError(
                '新建comment失败, 参数article_id格式错误 article_id = {}'.format(comment_article_id))
        res, ret = SENSITIVE_FILTER.filter(message)
        if res is False:
            raise ValidationError('新建失败，内容含有敏感词：' + ret)
        try:
            create_comment = CommentStore(comment_message=message, comment_article_id=comment_article_id,
                                          comment_publisher_id=comment_publisher.id)
            create_comment.save()
            return create_comment
        except Exception as e:
            raise e

    def get_comment_by_article(self, article_id, *args, **kwargs):
        """
        获取评论
        """
        return CommentStore.objects.filter(comment_article_id=article_id)

    def has_commented(self, user, comment, *args, **kwargs):
        """
        是否发表了该评论
        """
        if not user:
            return False
        return user.id == comment.comment_publisher.id

    def delete(self, user, comment_id, *args, **kwargs):
        """
        删除评论
        """
        delete_comment = get_object_or_404(CommentStore, id=comment_id)
        if delete_comment.comment_publisher_id == user.id:
            delete_comment.delete()
        else:
            raise PermissionDenied('没有删除评论权限')
        return True


COMMENT_SERVICE = CommentService()
