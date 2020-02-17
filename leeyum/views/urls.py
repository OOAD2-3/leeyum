from django.urls import path

from leeyum.views.user import UserCommonViewSet, UserViewSet

urlpatterns = [
    path('user/captcha/', UserCommonViewSet.as_view({'get': 'get_captcha'})),

    path('user/login/', UserViewSet.as_view({'post': 'login'})),
    path('user/logout/', UserViewSet.as_view({'get': 'logout'})),
]
