from datetime import date

from django.db import IntegrityError
from django.db.models import F

from leeyum.domain.models import ActionDefinition, ActionTimeRecorder, ArticleStore

__all__ = ('ACTION_SERVICE',)

from leeyum.infra.redis import func_cache

from leeyum.resource.exception import ActionRecordException


class ActionService(object):
    CATEGORY_TYPE = 'category'
    ARTICLE_TYPE = 'article'
    HOT_WORD_TYPE = 'hot_word'
    ALLOW_ACTION_TYPE = [CATEGORY_TYPE, ARTICLE_TYPE, HOT_WORD_TYPE]

    def record(self, action_type, record_data, user_id):
        if not self._check_action_type(action_type):
            raise ActionRecordException(message='action type is wrong:{}'.format(action_type))

        try:
            action_definition = ActionDefinition.objects. \
                create(action_type=action_type, record_data=record_data, user_id=user_id)
        except IntegrityError as e:
            action_definition = ActionDefinition.objects. \
                get(action_type=action_type, record_data=record_data, user_id=user_id)

        today = date.today()

        # 取出今天的记录
        action_recorder = action_definition.actions.filter(record_date__gte=today).first()
        if not action_recorder:
            latest_recorder = action_definition.actions.filter(record_date__lte=today).reverse().first()
            delta_ttl = (today - latest_recorder.record_date).days if latest_recorder else 0
            history_week_count = \
                latest_recorder.week_count if latest_recorder and (delta_ttl + latest_recorder.week_ttl) <= 7 else 0
            history_month_count = \
                latest_recorder.month_count if latest_recorder and (delta_ttl + latest_recorder.week_ttl) <= 30 else 0
            history_total_count = \
                latest_recorder.total_count if latest_recorder else 0

            history_week_ttl = \
                latest_recorder.week_ttl + 1 if latest_recorder and (delta_ttl + latest_recorder.week_ttl) < 7 else 1
            history_month_ttl = \
                latest_recorder.month_ttl + 1 if latest_recorder and (delta_ttl + latest_recorder.week_ttl) < 30 else 1
            # todo unique限制抛出异常处理
            action_recorder = ActionTimeRecorder.objects.create(action_definition=action_definition,
                                                                week_count=history_week_count,
                                                                month_count=history_month_count,
                                                                total_count=history_total_count,
                                                                week_ttl=history_week_ttl,
                                                                month_ttl=history_month_ttl)

        action_recorder.day_count = F('day_count') + 1
        action_recorder.week_count = F('week_count') + 1
        action_recorder.month_count = F('month_count') + 1
        action_recorder.total_count = F('total_count') + 1
        action_recorder.save()
        return action_recorder

    def _check_action_type(self, action_type):
        return action_type in self.ALLOW_ACTION_TYPE

    @func_cache('retrieve_hot_word', expired_time=60 * 60)
    def retrieve_hot_word(self, number=10, user_id=None):
        hot_words = \
            self.analyze_personal_data(user_id=user_id, action_type=self.HOT_WORD_TYPE, number=number) \
            if user_id else self.analyze_global_data(action_type=self.HOT_WORD_TYPE, number=number)
        res = []
        for item in hot_words:
            res.append(item.record_data)

        return res

    @func_cache('retrieve_highest_click_category', expired_time=60 * 60)
    def retrieve_highest_click_category(self, number=10, user_id=None):
        highest_click_category = \
            self.analyze_personal_data(user_id=user_id, action_type=self.CATEGORY_TYPE, number=number) \
            if user_id else self.analyze_global_data(action_type=self.CATEGORY_TYPE, number=number)
        res = []
        for item in highest_click_category:
            res.append(item.record_data)

        return res

    @func_cache('retrieve_highest_click_article', expired_time=60 * 60)
    def retrieve_highest_click_article(self, number=10, user_id=None):
        highest_click_category = \
            self.analyze_personal_data(user_id=user_id, action_type=self.ARTICLE_TYPE, number=number) \
            if user_id else self.analyze_global_data(action_type=self.ARTICLE_TYPE, number=number)
        res = []
        for item in highest_click_category:
            res.append(item.record_data)

        return res

    def analyze_highest_click_article(self, number=10, user_id=None):
        article_ids = self.retrieve_highest_click_article(number, user_id)

        keywords = []
        categories = []
        tags = []
        article_list = ArticleStore.objects.filter(id__in=article_ids)
        for article in article_list:
            article.concrete_article()
            keywords.extend(article.abstract)
            categories.append(article.category_id)
            tags.extend(article.tags)

        keywords = list(set(keywords))
        categories = list(set(categories))
        tags = list(set(tags))

        return keywords, categories, tags

    def analyze_global_data(self, action_type, number):
        sql = """
        select leeyum_action_definition.id, leeyum_action_definition.record_data, SUM(temp_recorder.month_count) as sum_month_count
        from (select * from leeyum_action_time_recorder where id in (select max(id) from leeyum_action_time_recorder group by action_definition_id)) as temp_recorder
        left join leeyum_action_definition
        on temp_recorder.action_definition_id=leeyum_action_definition.id
        where leeyum_action_definition.action_type="{action_type}"
        group by leeyum_action_definition.record_data
        order by sum_month_count DESC LIMIT {number};
        """.format(action_type=action_type, number=number)

        return ActionDefinition.objects.raw(sql)

    def analyze_personal_data(self, user_id, action_type, number):
        sql = """
        select leeyum_action_definition.id, leeyum_action_definition.record_data, SUM(temp_recorder.month_count) as sum_month_count
        from (select * from leeyum_action_time_recorder where id in (select max(id) from leeyum_action_time_recorder group by action_definition_id)) as temp_recorder
        left join leeyum_action_definition
        on temp_recorder.action_definition_id=leeyum_action_definition.id
        where leeyum_action_definition.action_type="{action_type}" and leeyum_action_definition.user_id={user_id}
        group by leeyum_action_definition.record_data
        order by sum_month_count DESC LIMIT {number};
        """.format(user_id=user_id, action_type=action_type, number=number)

        return ActionDefinition.objects.raw(sql)


ACTION_SERVICE = ActionService()
