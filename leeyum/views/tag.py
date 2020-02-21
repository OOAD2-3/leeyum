from rest_framework.exceptions import ValidationError

from leeyum.domain.models import TagStore
from leeyum.domain.service.tag import TAG_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class TagSerializer(BaseSerializer):
    class META:
        model = TagStore
        fields = ('__all__',)


class TagViewSet(BaseViewSet):

    def create(self, request):
        name = request.json_data.get('name')
        intro = request.json_data.get('intro')
        tag = TAG_SERVICE.create(name=name, intro=intro)
        return JSONResponse(data={'tag_name': tag.name})

    def update(self, request):
        tag_id = request.json_data.get('tag_id')
        name = request.json_data.get('name')
        intro = request.json_data.get('intro')
        tag, update_fields = TAG_SERVICE.update(tag_id=tag_id, name=name, intro=intro)
        return JSONResponse(data={'tag_id': tag_id, 'update_fields': update_fields})

    def list(self, request):
        pass

    def delete(self, request):
        tag_id = request.DELETE.get('tag_id')
        delete_tag = TAG_SERVICE.delete(tag_id=tag_id)
        return JSONResponse(data={'delete_tag_name': delete_tag.name})
