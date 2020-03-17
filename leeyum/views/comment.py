from rest_framework.exceptions import NotAuthenticated

from leeyum.domain.service.comment import COMMENT_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class CommentSerializer(BaseSerializer):
    pass


class CommentViewSet(BaseViewSet):

    def create(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")
        comment_message = request.json_data.get('comment_message')
        comment_article_id = request.json_data.get('article_id')

        comment = COMMENT_SERVICE \
            .create(message=comment_message, comment_article_id=int(comment_article_id), comment_publisher=request.user)
        return JSONResponse(data={'comment_id': comment.id})

    def list(self, request):
        user = request.user
        article_id = request.GET.get('article_id')
        comment_list = []
        comments = COMMENT_SERVICE.get_comment_by_article(article_id=article_id)
        for comment in comments:
            dict_res = ({'comment_id': comment.id, 'publisher_name': comment.comment_publisher.username,
                        'comment_message': comment.comment_message, 'report_level': comment.report_level})
            dict_res['has_commented'] = COMMENT_SERVICE.has_commented(user=user, comment=comment)
            comment_list.append(dict_res)
        return JSONResponse(data=comment_list)

    def delete(self, request):
        if not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated("身份未认证")
        user = request.user
        comment_id = request.GET.get('comment_id')
        COMMENT_SERVICE.delete(user=user, comment_id=comment_id)
        return JSONResponse(message='delete success')
