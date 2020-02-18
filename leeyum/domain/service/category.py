from django.db.models import Q

from leeyum.domain.models import CategoryStore


__all__ = ('CATEGORY_SERVICE',)


class CategoryService(object):
    """
    信息
    """
    def create(self, *args, **kwargs):
        pass

    def get_one(self, *args, **kwargs):
        q = Q()

        category_id = kwargs.get('category_id')
        if category_id:
            q &= Q(id=category_id)

        category_model = CategoryStore.objects.filter(q).first()
        return category_model


CATEGORY_SERVICE = CategoryService()
