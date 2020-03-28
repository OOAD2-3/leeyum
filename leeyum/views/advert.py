from rest_framework.exceptions import ValidationError, NotAuthenticated

from leeyum.domain.models import AdvertStore
from leeyum.domain.service.advert import ADVERT_SERVICE
from leeyum.domain.service.user import USER_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class AdvertSerializer(BaseSerializer):
    class META:
        model = AdvertStore
        fields = ('__all__',)


class AdvertViewSet(BaseViewSet):

    def retrieve(self, request):
        """
        广告详情
        """
        reader = request.user if bool(request.user and request.user.is_authenticated) else None
        advert_id = request.GET.get('id')
        advert = ADVERT_SERVICE.get_details(advert_id)

        dict_res = advert.to_dict(exclude=('publisher', 'gmt_modified', 'gmt_created', 'viewed_times'))
        # 发布者信息
        publisher = advert.publisher.to_dict(fields=('username', 'phone_number'))
        dict_res['publisher'] = publisher

        return JSONResponse(data=dict_res)
