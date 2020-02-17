from django.urls import path

from leeyum.views.user import UserCommonViewSet

urlpatterns = [
    path('user/captcha/', UserCommonViewSet.as_view({'get': 'get_captcha'}))
]