from leeyum.domain.models import CategoryStore
from leeyum.domain.service.category import CATEGORY_SERVICE
from leeyum.views import BaseViewSet, BaseSerializer, JSONResponse


class CategorySerializer(BaseSerializer):
    class META:
        model = CategoryStore
        fields = ('__all__',)


class CategoryViewSet(BaseViewSet):

    def create(self, request):
        name = request.json_data.get('name')
        intro = request.json_data.get('intro')
        parent = request.json_data.get('parent')
        category = CATEGORY_SERVICE.create(name=name, intro=intro, parent=parent)
        return JSONResponse(data={'category_id': category.id})

    def update(self, request):
        category_id = request.json_data.get('category_id')
        name = request.json_data.get('name')
        intro = request.json_data.get('intro')
        parent = request.json_data.get('parent')
        category, update_fields = CATEGORY_SERVICE.update(category_id=category_id, name=name, intro=intro, parent=parent)
        return JSONResponse(data={'category_id': category_id, 'update_fields': update_fields})

    def delete(self, request):
        pass

    def list(self, request):
        pass
