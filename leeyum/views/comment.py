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
        comment_article_id = request.json_data.get('comment_article_id')
        comment_parent_id = request.json_data.get('comment_parent_id')

        comment = COMMENT_SERVICE \
            .create(message=comment_message, comment_article_id=comment_article_id, comment_publiser=request.user,
                    comment_parent_id=comment_parent_id)
        return JSONResponse(data={'comment_id': comment.id})

    def list(self, request):
        article_id = request.GET.get('article_id')
        comment_list = COMMENT_SERVICE.get_comment_by_article(article_id=article_id)
        return JSONResponse(data=comment_list)

    def delete(self, request):
        comment_id = request.GET.get('comment_id')
        COMMENT_SERVICE.delete(comment_id=comment_id)
        return JSONResponse(message='delete success')
