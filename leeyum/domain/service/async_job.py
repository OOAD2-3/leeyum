from leeyum.domain.service.action import ACTION_SERVICE
from mysite import celery_app
import jieba


@celery_app.task
def record_search_word(keyword, user_id):
    # keyword 埋点
    cut_word_list = jieba.cut(keyword, cut_all=False)
    for cut_word in cut_word_list:
        ACTION_SERVICE.record(ACTION_SERVICE.HOT_WORD_TYPE, cut_word, user_id=user_id)
    return '/'.join(cut_word_list)
