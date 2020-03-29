from django.shortcuts import get_object_or_404
import random

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
        step = 1
        adverts = AdvertStore.objects.all()
        for advert in adverts:
            advert.concrete_advert()
            dict_res = advert.to_dict(exclude=('publisher', 'gmt_modified', 'gmt_created'))
            dict_res['category'] = ['广告', '广告']
            if step < len(article_list):
                article_list.insert(step, dict_res)
                step += random.randint(5, 10)
            else:
                article_list.append(dict_res)

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
