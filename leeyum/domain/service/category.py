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

    def list(self, category_id=-1, *args, **kwargs):
        """
        列出该类目及其子类目（多级）
        未传category_id，则列出所有类目（层级关系）
        """
        category_list = []
        sub_category_list = []
        if category_id == -1:
            categories = CategoryStore.objects.filter(parent__isnull=True)
            for cat in categories:
                category_list.extend(self.list(category_id=cat.id))
        else:
            category = get_object_or_404(CategoryStore, id=category_id)
            category_list.append({'category_id': category.id, 'category_name': category.name, 'category_intro': category.intro, 'sub_category_list': sub_category_list})
            sub_categories = category.sub_category.all()
            for sub_cat in sub_categories:
                sec_sub_category_list = []
                sub_category_list.append({'category_id': sub_cat.id, 'category_name': sub_cat.name, 'category_intro': sub_cat.intro, 'sub_category_list': sec_sub_category_list})
                for sec_sub_cat in sub_cat.sub_category.all():
                    sec_sub_category_list.extend(self.list(category_id=sec_sub_cat.id))
        return category_list

    def get_parent_category(self, category_id, *args, **kwargs):
        """
        获取类目信息及所属父类目
        """
        category = get_object_or_404(CategoryStore, id=category_id)
        parent_category_list = [category.name]
        parent_id = category.parent_id
        while parent_id:
            parent_category = get_object_or_404(CategoryStore, id=parent_id)
            parent_category_list.append(parent_category.name)
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
