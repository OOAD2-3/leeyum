from rest_framework.exceptions import NotAuthenticated

from leeyum.domain.service.report import REPORT_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class ReportSerializer(BaseSerializer):
    pass


class ReportViewSet(BaseViewSet):

    def create(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")
        article_id = request.json_data.get('article_id')
        comment_id = request.json_data.get('comment_id')
        report_reason = request.json_data.get('report_reason', [])
        report = REPORT_SERVICE.create(reporter=request.user, article_id=article_id,
                                       comment_id=comment_id, report_reason=report_reason)
        return JSONResponse(data={'report_id': report.id})

    def cancel(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")
        user = request.user
        report_id = request.GET.get('report_id')
        REPORT_SERVICE.cancel(user=user, report_id=report_id)
        return JSONResponse(message='cancel report success')

    def get_reported_times(self, request):
        article_id = request.GET.get('article_id')
        comment_id = request.GET.get('comment_id')
        reported_times = REPORT_SERVICE.get_reported_times(article_id=article_id, comment_id=comment_id)
        return JSONResponse(data={'reported_times': reported_times})
