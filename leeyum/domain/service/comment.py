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
        comment_parent_id = kwargs.get('comment_parent_id')
        if not comment_article_id or type(comment_article_id) is not int:
            raise ValidationError(
                '新建comment失败, 参数comment_article_id格式错误 comment_article_id = {}'.format(comment_article_id))
        if SENSITIVE_FILTER.filter(message) is False:
            raise ValidationError('新建失败，评论含有敏感词！')
        try:
            create_comment = CommentStore(comment_message=message, comment_article_id=comment_article_id,
                                          comment_parent_id=comment_parent_id,
                                          comment_publisher_id=comment_publisher.id)
            create_comment.save()
            return create_comment
        except Exception as e:
            raise e

    def get_comment_by_article(self, article_id, *args, **kwargs):
        """
        article下的所有评论（树形结构）
        """
        comments = CommentStore.objects.filter(Q(comment_article_id=article_id) & Q(comment_parent__isnull=True))
        comment_list = []
        for comment in comments:
            publisher = get_object_or_404(UserStore, id=comment.comment_publisher_id)
            sub_comment_list = []
            comment_list.append({
                'comment_id': comment.id,
                'publisher_name': publisher.username,
                'comment_message': comment.comment_message,
                'sub_comment_list': sub_comment_list})
            for sub_com in comment.sub_comment.all():
                sub_comment_list.extend(self.get_comment_by_parent_comment(comment_id=sub_com.id))
        return comment_list

    def get_comment_by_parent_comment(self, comment_id, *args, **kwargs):
        """
        comment及其子comment（树形结构）
        """
        comment_list = []
        sub_comment_list = []
        comment = get_object_or_404(CommentStore, id=comment_id)
        comment_list.append({
            'comment_id': comment.id,
            'publisher_id': comment.comment_publisher_id,
            'comment_message': comment.comment_message,
            'sub_comment_list': sub_comment_list})
        sub_comments = comment.sub_comment.all()
        for sub_com in sub_comments:
            sec_sub_comment_list = []
            sub_comment_list.append({
                'comment_id': sub_com.id,
                'publisher_id': sub_com.comment_publisher_id,
                'comment_message': sub_com.comment_message,
                'sub_comment_list': sec_sub_comment_list})
            for sub_sub_com in sub_com.sub_comment.all():
                sec_sub_comment_list.extend(self.get_comment_by_parent_comment(comment_id=sub_sub_com.id))
        return comment_list

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
