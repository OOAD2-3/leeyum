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
        parent_id = request.json_data.get('parent_id')
        category = CATEGORY_SERVICE.create(name=name, intro=intro, parent_id=parent_id)
        return JSONResponse(data={'category_id': category.id})

    def update(self, request):
        category_id = request.json_data.get('category_id')
        name = request.json_data.get('name')
        intro = request.json_data.get('intro')
        parent_id = request.json_data.get('parent_id')
        category, update_fields = CATEGORY_SERVICE.update(category_id=category_id, name=name, intro=intro, parent_id=parent_id)
        return JSONResponse(data={'category_id': category_id, 'update_fields': update_fields})

    def delete(self, request):
        pass

    def list_sub_categories(self, request):
        """
        列出该类目下的子类目
        """
        category_id = request.GET.get('category_id')
        category, sub_category_list = CATEGORY_SERVICE.list_sub_categories(category_id=category_id)
        return JSONResponse(data=
                            {'category_id': category.id,
                             'category_name': category.name,
                             'sub_category_list': sub_category_list})

    def get_parent_category(self, request):
        """
        根据子类目获取父类目信息
        """
        category_id = request.GET.get('category_id')
        category, parent_category_list = CATEGORY_SERVICE.get_parent_category(category_id=category_id)
        return JSONResponse(data={'category_id': category.id,
                                  'category_name': category.name,
                                  'category_intro': category.intro,
                                  'parent_category_list': parent_category_list})
