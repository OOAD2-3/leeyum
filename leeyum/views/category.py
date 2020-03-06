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
        category, update_fields = CATEGORY_SERVICE.update(category_id=category_id, name=name, intro=intro,
                                                          parent_id=parent_id)
        return JSONResponse(data={'category_id': category_id, 'update_fields': update_fields})

    def delete(self, request):
        pass

    def list(self, request):
        """
        列出该类目及其子类目（多级）
        未传category_id，则列出所有类目（层级关系）
        """
        # 若无category_id传进来，默认为-1，即一级目录
        category_id = request.GET.get('category_id', -1)
        if not category_id:
            category_id = -1
        category_list = CATEGORY_SERVICE.list(category_id=category_id)
        return JSONResponse(data=category_list)

    def get_parent_category(self, request):
        """
        获取类目信息及所属父类目
        """
        category_id = request.GET.get('category_id')
        category, parent_category_list = CATEGORY_SERVICE.get_parent_category(category_id=category_id)
        return JSONResponse(data={'category_id': category.id,
                                  'category_name': category.name,
                                  'category_intro': category.intro,
                                  'parent_category_list': parent_category_list})

    def list_leaves(self, request):
        """
        通过category_id 获取该节点的所有最底层叶子类目
        """
        category_id = request.GET.get('category_id')
        leave_list = CATEGORY_SERVICE.get_leaves(category_id=category_id)
        return JSONResponse(data=leave_list)
