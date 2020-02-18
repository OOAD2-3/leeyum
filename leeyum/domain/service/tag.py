__all__ = ('TAG_SERVICE',)

from django.db.models import Q

from leeyum.domain.models import TagStore


class TagService(object):
    def create(self):
        pass

    def get_one(self, *args, **kwargs):
        if kwargs.get('tag_id'):
            pass

    def get_many(self, *args, **kwargs):
        # 查询器
        q = Q()

        tags_id = kwargs.get('tags_id', [])
        if tags_id:
            q &= Q(id__in=tags_id)

        tags_model = TagStore.objects.filter(q)
        return list(tags_model)


TAG_SERVICE = TagService()
