from django.db.models import Q

from django.shortcuts import get_object_or_404
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
        parent = kwargs.get('parent')
        try:
            create_category = CategoryStore(name=name, intro=intro)
            if parent:
                create_category.parent.add(*parent)

            create_category.save()
            return create_category
        except Exception as e:
            raise e

    def update(self, category_id, *args, **kwargs):
        """
        修改类目
        """
        update_category = get_object_or_404(CategoryStore, id=category_id)

        fields = ['name', 'intro', 'parent']
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

    def list(self, *args, **kwargs):
        """
        展示相同父类目下的类目
        """
        q = Q()

    def get_parent(self, *args, **kwargs):
        pass


CATEGORY_SERVICE = CategoryService()
