from django.db.models import Q

from leeyum.domain.models import CommentStore
from django.shortcuts import get_object_or_404
from django.db.models import Q


__all__ = ('COMMENT_SERVICE',)


class CommentService(object):
    """
    信息
    """
    def create(self, message, comment_article_id, comment_publiser, *args, **kwargs):
        """
        新建评论
        """
        comment_parent_id = kwargs.get('comment_parent_id')
        try:
            create_comment = CommentStore(comment_message=message, comment_article_id=comment_article_id, comment_parent_id=comment_parent_id)
            create_comment.comment_publisher_id = comment_publiser.id if comment_publiser.id is not None else 1
            create_comment.comment_type = CommentStore.NORMAL_COMMENT
            create_comment.save()
            return create_comment
        except Exception as e:
            raise e

    def get_comment_by_article(self, article_id, *args, **kwargs):
        comments = CommentStore.objects.filter(Q(comment_article_id=article_id) & Q(comment_parent__isnull=True))
        comment_list = []
        for comment in comments:
            sub_comment_list = []
            comment_list.append({
                                'comment_id': comment.id,
                                'publisher_id': comment.comment_publisher_id,
                                'comment_message': comment.comment_message,
                                'sub_comment_list': sub_comment_list})
            for sub_com in comment.sub_comment.all():
                sub_comment_list.extend(self.get_comment_by_parent_comment(comment_id=sub_com.id))
        return comment_list

    def get_comment_by_parent_comment(self, comment_id, *args, **kwargs):
        comment_lsit = []
        sub_comment_list = []
        comment = get_object_or_404(CommentStore, id=comment_id)
        comment_lsit.append({
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
        return comment_lsit

    def delete(self, comment_id, *args, **kwargs):
        delete_comment = get_object_or_404(CommentStore, id=comment_id)
        if delete_comment:
            delete_comment.delete()
        return True


COMMENT_SERVICE = CommentService()
