from django.urls import path

from leeyum.views.user import UserViewSet

urlpatterns = [
    # 实验url
    path('user/test2/', UserViewSet.as_view({'get': 'get_captcha'}))
]