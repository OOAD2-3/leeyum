from leeyum.domain.service.action import ACTION_SERVICE
from leeyum.views import BaseViewSet, JSONResponse


class ActionViewSet(BaseViewSet):

    def record(self, request):
        action_type = str(request.json_data.get('action_type'))
        record_data = str(request.json_data.get('record_data'))

        if not bool(request.user and request.user.is_authenticated):
            return JSONResponse(data={}, message="用户未登陆不做记录")

        res = ACTION_SERVICE.record(action_type, record_data, request.user.id)
        return JSONResponse(data=res.to_dict(exclude=('action_definition',)))
