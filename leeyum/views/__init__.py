# Create your views here.
from django.http import JsonResponse
from rest_framework import viewsets, serializers


class BaseViewSet(viewsets.ViewSet):
    pass


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class JSONResponse(JsonResponse):
    def __init__(self, data=None, code=200, message='success'):
        if data is None:
            data = {}

        res = {
            'code': code,
            'data': data,
            'message': message
        }
        JsonResponse.__init__(self, data=res)


class ErrorResponse(JsonResponse):
    def __init__(self, data=None, status=400, message='error'):
        if data is None:
            data = {}

        err_res = {
            'code': status,
            'data': data,
            'message': message
        }
        JsonResponse.__init__(self, data=err_res, status=status)
