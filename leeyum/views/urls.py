from django.urls import path

from leeyum.views.action import ActionViewSet
from leeyum.views.front_config import FrontConfigViewSet
from leeyum.views.report import ReportViewSet
from leeyum.views.tag import TagViewSet
from leeyum.views.user import UserCommonViewSet, UserViewSet
from leeyum.views.article import ArticleViewSet, ArticleRelationViewSet
from leeyum.views.comment import CommentViewSet
from leeyum.views.category import CategoryViewSet

urlpatterns = [
    path('user/captcha/', UserCommonViewSet.as_view({'get': 'get_captcha'})),

    path('user/login/', UserCommonViewSet.as_view({'post': 'login'})),
    path('user/logout/', UserViewSet.as_view({'get': 'logout'})),
    path('user/settings/student_authenticate/', UserViewSet.as_view({'post': 'student_authentication'})),
    # path('user/settings/accept/', UserViewSet.as_view({'post': 'accept_settings'})),
    path('user/settings/update/', UserViewSet.as_view({'put': 'update'})),

    path('user/details/', UserViewSet.as_view({'get': 'retrieve'})),
    path('user/published/', UserViewSet.as_view({'get': 'list_published_article'})),
    path('user/like/', UserViewSet.as_view({'post': 'add_like_article', 'get': 'list_like_article', 'delete': 'delete_like_article'})),
    path('user/liked/', UserViewSet.as_view({'get': 'get_liked_times'})),
    path('user/viewed/', UserViewSet.as_view({'get': 'list_viewed_article', 'delete': 'clear_viewed_article'})),
    path('user/teams/', UserViewSet.as_view({'get': 'list_teams'})),

    path('file/upload/', ArticleViewSet.as_view({'post': 'upload_file'})),

    path('article/', ArticleViewSet.as_view({'post': 'create', 'put': 'update', 'get': 'list', 'delete': 'take_off'})),
    path('article/details/', ArticleViewSet.as_view({'get': 'retrieve'})),
    path('article/join_team/', ArticleViewSet.as_view({'put': 'join_team'})),
    path('article/leave_team/', ArticleViewSet.as_view({'put': 'leave_team'})),
    path('article/publish_recommend/', ArticleRelationViewSet.as_view({'get': 'get_publish_recommend'})),

    path('article/hot_words/', ArticleRelationViewSet.as_view({'get': 'get_hot_word'})),

    path('tag/', TagViewSet.as_view({'post': 'create', 'put': 'update', 'delete': 'delete'})),
    path('tag/all/', TagViewSet.as_view({'get': 'get_all_tags'})),

    path('category/', CategoryViewSet.as_view({'post': 'create', 'get': 'list'})),

    path('comment/', CommentViewSet.as_view({'post': 'create', 'get': 'list', 'delete': 'delete'})),

    path('report/', ReportViewSet.as_view({'post': 'create','delete': 'cancel', 'get': 'get_reported_times'}))
]

urlpatterns += [
    path('action/record/', ActionViewSet.as_view({'post': 'record'}))
]

urlpatterns += [
    path('front_config/express_news/', FrontConfigViewSet.as_view({'get': 'express_news'})),
    path('front_config/page_config/', FrontConfigViewSet.as_view({'get': 'page_config'}))
]
