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

        if code != 200:
            message = 'error'

        res = {
            'code': code,
            'data': data,
            'message': message
        }
        JsonResponse.__init__(self, data=res)
