from django.db.models import Q

from leeyum.domain.models import CommentStore


__all__ = ('COMMENT_SERVICE',)


class CommentService(object):
    """
    信息
    """
    def create(self, *args, **kwargs):
        pass

    def get_list_by_article(self, *args, **kwargs):
        pass


COMMENT_SERVICE = CommentService()
