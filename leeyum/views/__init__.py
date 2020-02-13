# Create your views here.
from rest_framework import viewsets, serializers


class BaseViewSet(viewsets.ModelViewSet):
    pass


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
