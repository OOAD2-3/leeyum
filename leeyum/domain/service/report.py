from django.db.models import Q

import json
from rest_framework.exceptions import PermissionDenied
from leeyum.domain.models import ReportStore, UserStore, ArticleStore, CommentStore
from django.shortcuts import get_object_or_404


__all__ = ('REPORT_SERVICE',)


class ReportService(object):
    """
    举报模块
    """
    def create(self, article_id, report_reason, reporter, *args, **kwargs):
        """
        举报信息或评论
        """
        comment_id = kwargs.get('comment_id')
        if not comment_id:
            try:
                create_report = ReportStore(report_article_id=article_id, reporter_id=reporter.id)
                create_report.report_reason = json.dumps(report_reason) if report_reason else "[]"
                create_report.save()
                article = get_object_or_404(ArticleStore, id=article_id)
                reported_times = self.get_reported_times_by_article(article_id=article_id)
                if reported_times >= 20:
                    article.report_level = ArticleStore.PROBLEM
                elif reported_times >= 50:
                    article.report_level = ArticleStore.DANGER
                return create_report
            except Exception as e:
                raise e
        else:
            try:
                create_report = ReportStore(report_article_id=article_id,
                                            report_comment_id=comment_id,
                                            reporter_id=reporter.id)
                create_report.report_reason = json.dumps(report_reason) if report_reason else "[]"
                create_report.save()
                comment = get_object_or_404(CommentStore, id=comment_id)
                reported_times = self.get_reported_times_by_comment(comment_id=comment_id)
                if reported_times >= 20:
                    comment.report_level = CommentStore.PROBLEM
                if reported_times >= 50:
                    comment.report_level = CommentStore.DANGER
                return create_report
            except Exception as e:
                raise e

    def get_reported_times(self, *args, **kwargs):
        article_id = kwargs.get('article_id')
        comment_id = kwargs.get('comment_id')
        reported_times = 0
        if article_id:
            reported_times = self.get_reported_times_by_article(article_id=article_id)
        if comment_id:
            reported_times = self.get_reported_times_by_comment(comment_id=comment_id)
        return reported_times

    def get_reported_times_by_article(self, article_id, *args, **kwargs):
        return ReportStore.objects.filter(Q(report_article_id=article_id) & Q(report_comment_id__isnull=True)).count()

    def get_reported_times_by_comment(self, comment_id, *args, **kwargs):
        return ReportStore.objects.filter(report_comment_id=comment_id).count()

    def get_reported_times_by_user(self, user, *args, **kwargs):
        """
        用户黑名单
        """
        article_reported_times = ArticleStore.objects.filter(Q(publisher_id=user.id) & Q(status=5)).conut()
        if article_reported_times >= 10:
            user.is_active = False
        else:
            user.is_active = True
        return user

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
