from django.db.models import Q

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from leeyum.domain.models import CategoryStore


__all__ = ('CATEGORY_SERVICE',)


class CategoryService(object):
    """
    信息
    """
    def create(self, name, intro, *args, **kwargs):
        """
        新建类目
        """
        parent_id = kwargs.get('parent_id')
        try:
            create_category = CategoryStore(name=name, intro=intro)
            create_category.parent_id = parent_id

            create_category.save()
            return create_category
        except Exception as e:
            raise e

    def update(self, category_id, *args, **kwargs):
        """
        修改类目
        """
        update_category = get_object_or_404(CategoryStore, id=category_id)

        fields = ['name', 'intro', 'parent_id']
        update_fields = []

        for f in fields:
            if kwargs.get(f):
                update_fields.append(f)
                value = kwargs.get(f)

                setattr(update_category, f, value)
        update_category.save()
        return update_category, update_fields

    def get_one(self, *args, **kwargs):
        q = Q()

        category_id = kwargs.get('category_id')
        if category_id:
            q &= Q(id=category_id)

        category_model = CategoryStore.objects.filter(q).first()
        return category_model

    def list_sub_categories(self, category_id, *args, **kwargs):
        """
        列出该类目下的子类目
        """
        category = get_object_or_404(CategoryStore, id=category_id)
        category_data = CategoryStore.objects.filter(parent_id=category_id).values('id', 'name', 'intro')
        sub_category_list = []
        for cat in category_data:
            sub_category_list.append({'id': cat['id'], 'name': cat['name'], 'intro': cat['intro']})
        return category, sub_category_list

    def get_parent_category(self, category_id, *args, **kwargs):
        """
        根据子类目获取所有父类目信息
        """
        category = get_object_or_404(CategoryStore, id=category_id)
        parent_category_list = []
        parent_id = category.parent_id
        while parent_id:
            parent_category = get_object_or_404(CategoryStore, id=parent_id)
            parent_category_list.append({'id': parent_category.id,
                                         'name': parent_category.name,
                                         'intro': parent_category.intro})
            parent_id = parent_category.parent_id
            continue

        parent_category_list.reverse()
        return category, parent_category_list

    def get_leaves(self, category_id):
        # todo
        # 通过category_id 获取该节点的所有最底层叶子类目
        # 若category_id已经是最底层直接返回 [category_id]
        # category_id格式错误或者找不到都返回空list
        return []


CATEGORY_SERVICE = CategoryService()
