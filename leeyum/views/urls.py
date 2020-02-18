from django.urls import path

from leeyum.views.user import UserCommonViewSet, UserViewSet
from leeyum.views.article import ArticleViewSet

urlpatterns = [
    path('user/captcha/', UserCommonViewSet.as_view({'get': 'get_captcha'})),
    path('user/login/', UserViewSet.as_view({'post': 'login'})),
    path('user/logout/', UserViewSet.as_view({'get': 'logout'})),

    path('article/', ArticleViewSet.as_view({'post': 'create', 'put': 'update', 'get': 'list'})),
]
