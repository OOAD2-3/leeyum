from leeyum.domain.service.action import ACTION_SERVICE
from leeyum.views import BaseViewSet, JSONResponse


class ActionViewSet(BaseViewSet):

    def record(self, request):
        reader = request.user if bool(request.user and request.user.is_authenticated) else None

        action_type = str(request.json_data.get('action_type'))
        record_data = str(request.json_data.get('record_data'))

        if reader:
            res = ACTION_SERVICE.record(action_type, record_data, request.user.id)
            return JSONResponse(data=res.to_dict(exclude=('action_definition',)))

        return JSONResponse(data={}, message="用户未登陆不做记录")
