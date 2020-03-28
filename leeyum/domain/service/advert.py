from django.shortcuts import get_object_or_404

from leeyum.domain.models import AdvertStore

__all__ = ('ADVERT_SERVICE',)


class AdvertService(object):
    """
    广告
    """
    def get_details(self, advert_id):
        """
        广告详情
        """
        advert = get_object_or_404(AdvertStore, id=advert_id)

        advert.concrete_advert()
        return advert

    def add_to_article(self, article_list, *args, **kwargs):
        """
        将广告插入到article中article
        5条信息中存在1条广告
        """
        step = 0
        adverts = AdvertStore.objects.all()
        for advert in adverts:
            advert.concrete_advert()
            article_list.insert(step, advert.to_dict())
            step += 5

        return article_list

    def get_all_advert(self):
        """
        获取所有广告
        """
        adverts = AdvertStore.objects.all()
        for advert in adverts:
            advert.concrete_advert()

        return adverts


ADVERT_SERVICE = AdvertService()
