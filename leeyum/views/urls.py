from django.urls import path

from leeyum.views.user import UserCommonViewSet, UserViewSet
from leeyum.views.article import ArticleViewSet
from leeyum.views.comment import CommentViewSet

urlpatterns = [
    path('user/captcha/', UserCommonViewSet.as_view({'get': 'get_captcha'})),
    path('user/login/', UserViewSet.as_view({'post': 'login'})),
    path('user/logout/', UserViewSet.as_view({'get': 'logout'})),

    path('file/upload/', ArticleViewSet.as_view({'post': 'upload_file'})),

    path('article/', ArticleViewSet.as_view({'post': 'create', 'put': 'update', 'get': 'list'})),
    path('article/details/', ArticleViewSet.as_view({'get': 'retrieve'})),


    path('comment/', CommentViewSet.as_view({'post': 'create', 'get': 'list'}))
]
