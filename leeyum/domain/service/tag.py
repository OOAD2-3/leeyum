__all__ = ('TAG_SERVICE',)

from django.db.models import Q
import json
from django.shortcuts import get_object_or_404
from leeyum.domain.models import TagStore


class TagService(object):
    def create(self, name, intro, *args, **kwargs):
        """
        新建标签
        """
        try:
            create_tag = TagStore(name=name, intro=intro)
            create_tag.save()
            return create_tag
        except Exception as e:
            raise e

    def update(self, tag_id, *args, **kwargs):
        """
        修改标签
        """
        update_tag = get_object_or_404(TagStore, id=tag_id)
        fields = ['name', 'intro']
        update_fields = []

        for f in fields:
            if kwargs.get(f):
                update_fields.append(f)
                value = kwargs.get(f)
                setattr(update_tag, f, value)
        update_tag.save()
        return update_tag, update_fields

    def delete(self, tag_id, *args, **kwargs):
        delete_tag = TagStore.objects.filter(id=tag_id)
        if delete_tag:
            delete_tag.delete()
        return delete_tag

    def get_one(self, *args, **kwargs):
        tag_id = kwargs.get('tag_id')
        try:
            if tag_id:
                tag = get_object_or_404(TagStore, tag_id)
                tag.intro = json.loads(tag.intro)
                return tag
        except Exception as e:
            raise e

    def get_many(self, *args, **kwargs):
        # 查询器
        q = Q()

        tags_id = kwargs.get('tags_id', [])
        if tags_id:
            q &= Q(id__in=tags_id)

        tags_model = TagStore.objects.filter(q)
        return list(tags_model)


TAG_SERVICE = TagService()
