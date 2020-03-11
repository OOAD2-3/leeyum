from django.db.models import Q

from rest_framework.exceptions import PermissionDenied
from leeyum.domain.models import ReportStore, UserStore, ArticleStore
from django.shortcuts import get_object_or_404

from leeyum.domain.service.user import USER_SERVICE

__all__ = ('REPORT_SERVICE',)


class ReportService(object):
    """
    举报模块
    """
    def create(self, report_reason, reporter, *args, **kwargs):
        """
        举报信息或评论
        """
        article_id = kwargs.get('article_id')
        comment_id = kwargs.get('comment_id')
        try:
            create_report = ReportStore(report_reason=report_reason, report_article_id=article_id,
                                        report_comment_id=comment_id, reporter_id=reporter.id)
            create_report.save()
            return create_report
        except Exception as e:
            raise e

    def get_reported_times(self, *args, **kwargs):
        article_id = kwargs.get('article_id')
        comment_id = kwargs.get('comment_id')
        reported_times = 0
        if article_id:
            reported_times = self.get_reported_times_by_article(article_id=article_id)
            # article黑名单
            if reported_times == 20:
                article = get_object_or_404(ArticleStore, id=article_id)
                article.status = ArticleStore.ES_ERROR_STATUS
        if comment_id:
            reported_times = self.get_reported_times_by_comment(comment_id=comment_id)
        return reported_times

    def get_reported_times_by_article(self, article_id, *args, **kwargs):
        return ReportStore.objects.filter(report_article_id=article_id).count()

    def get_reported_times_by_comment(self, comment_id, *args, **kwargs):
        return ReportStore.objects.filter(report_comment_id=comment_id).count()

    def get_reported_times_by_user(self, user, *args, **kwargs):
        # article_reported_times = ArticleStore.objects.filter(Q(publisher_id=user.id) & Q(status=2)).conut()
        # if article_reported_times == 10:
        #     user.is_active = False
        # return article_reported_times
        pass

    def cancel(self, user, report_id, *args, **kwargs):
        """
        取消举报
        """
        cancel_report = get_object_or_404(ReportStore, id=report_id)
        if cancel_report.reporter_id == user.id:
            cancel_report.delete()
        else:
            raise PermissionDenied('没有取消举报权限')
        return True


REPORT_SERVICE = ReportService()
