from datetime import datetime, date, timedelta

from django.db.models import F

from leeyum.domain.models import ActionDefinition, ActionTimeRecorder

__all__ = ('ACTION_SERVICE',)

from leeyum.resource.exception import ActionRecordException


class ActionService(object):
    ALLOW_ACTION_TYPE = ['category', 'article', 'hot_word']

    def record(self, action_type, record_data, user_id):
        if not self._check_action_type(action_type):
            raise ActionRecordException(message='action type is wrong:{}'.format(action_type))

        action_definition, is_create = ActionDefinition.objects. \
            get_or_create(action_type=action_type, record_data=record_data, user_id=user_id)

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


ACTION_SERVICE = ActionService()
