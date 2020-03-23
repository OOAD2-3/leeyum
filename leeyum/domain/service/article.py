from leeyum.domain.service.action import ACTION_SERVICE
from leeyum.infra.sensitiveFilter import SENSITIVE_FILTER

__all__ = ('ARTICLE_SERVICE', 'ARTICLE_INDEX_SERVICE')

import json
import jieba.analyse

import requests
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from leeyum.domain.models import ArticleStore, FileUploadRecorder
from leeyum.domain.service.category import CATEGORY_SERVICE
from leeyum.domain.utils import utc_to_datetime, random_list_filter, ShowType
from leeyum.infra.aliCloud import ALI_STORAGE
from leeyum.resource.exception import FileTypeException, FileTooBigException, JoinTeamException


class ArticleService(object):
    """
    信息
    """

    def get_details(self, article_id):
        article = get_object_or_404(ArticleStore, id=article_id)

        article.concrete_article()
        return article

    def create(self, title, pic_urls, content_details, creator, category_id, *args, **kwargs):
        """
        新建
        """
        tags = kwargs.get('tags', [])

        if not category_id or type(category_id) is not int:
            raise ValidationError('新建article失败, 参数category_id格式错误 category_id = {}'.format(category_id))

        if SENSITIVE_FILTER.filter(title) is False:
            raise ValidationError('新建失败，标题含有敏感词！')
        if SENSITIVE_FILTER.filter(json.dumps(content_details)) is False:
            raise ValidationError('新建失败，内容含有敏感词！')

        try:
            create_article = ArticleStore(title=title, publisher_id=creator.id)
            create_article.abstract = jieba.analyse.extract_tags(
                "{},{},{}".format(create_article.title, content_details.get('body'), content_details.get('place', '')),
                topK=5)
            create_article.pic_urls = json.dumps(pic_urls)
            create_article.content = create_article.format_content(content_details)
            create_article.tags = json.dumps(tags) if tags else "[]"
            create_article.category_id = category_id
            create_article.status = ArticleStore.NORMAL_STATUS
            create_article.save()

            # 如果是组队，记录组队关系
            if create_article.is_team_type():
                create_article.team_members.add(creator)

            # 将文件置为已使用
            FileUploadRecorder.use_these_files(pic_urls)

            # 同步至es中
            ARTICLE_INDEX_SERVICE.publish(create_article)
            return create_article
        except Exception as e:
            raise e

    def update(self, article_id, *args, **kwargs):
        """
        TODO 有问题 不用这个功能
        """
        update_article = get_object_or_404(ArticleStore, id=article_id)
        update_article.concrete_article()

        fields = ['title', 'content', 'pic_urls', 'tags', 'category_id']
        update_fields = []

        for f in fields:
            if kwargs.get(f):
                update_fields.append(f)
                value = kwargs.get(f)
                if f == 'title':
                    if SENSITIVE_FILTER.filter(f) is False:
                        raise ValidationError('新建失败，标题含有敏感词！')
                if f == 'content':
                    if SENSITIVE_FILTER.filter(f) is False:
                        raise ValidationError('新建失败，内容含有敏感词！')
                    value = update_article.format_content(content_details=value)
                if f == 'pic_urls':
                    self.diff_pic(update_article, pic_urls=value)
                    value = json.dumps(value)
                if f == 'tags':
                    value = json.dumps(value)

                setattr(update_article, f, value)

        update_article.save()
        return update_article, update_fields

    def delete(self, article_id):
        """
        逻辑删除
        """
        article = get_object_or_404(ArticleStore, id=article_id)
        try:
            ARTICLE_INDEX_SERVICE.delete(article_id)
        except Exception as e:
            article.status = ArticleStore.ES_ERROR_STATUS
            article.save()
            raise e

        FileUploadRecorder.abandon_these_files(json.loads(article.pic_urls))
        article.status = ArticleStore.DELETE_STATUS
        article.save()

    def upload_pic(self, pic_file, uploader):
        # 限制大小 限制类型
        restricted_type = ('image/png', 'image/jpg', 'image/jpeg')
        max_size = 1024 * 1024 * 10
        if pic_file.content_type not in restricted_type:
            raise FileTypeException(message='file name: {}'.format(pic_file.name))
        if pic_file.size > max_size:
            raise FileTooBigException(message='file name: {}'.format(pic_file.name))

        ali_result = ALI_STORAGE.upload(file_name=pic_file.name, file=pic_file, uploader=uploader.username)
        pic_url = ali_result.resp.response.url

        file_upload_recorder, create = FileUploadRecorder \
            .objects.update_or_create(file_url=pic_url, defaults={'file_name': pic_file.name, 'is_used': False})

        return file_upload_recorder

    def diff_pic(self, article, pic_urls):
        """
        修改文件使用记录
        """

        deleted_pic_urls = [item for item in article.pic_urls if item not in pic_urls]
        add_pic_urls = [item for item in pic_urls if item not in article.pic_urls]

        FileUploadRecorder.abandon_these_files(deleted_pic_urls)
        FileUploadRecorder.use_these_files(add_pic_urls)

    def show(self, show_type, user=None, category=None, tags=None, order_type=None):
        """
        首页-兴趣推荐 & 本月热门 & 分类目
        """
        if show_type == ShowType.interest:
            return self._show_interest_recommend(user.id) if user else self._show_interest_recommend(-1)
        elif show_type == ShowType.monthly_hot:
            return self._show_monthly_recommend()
        elif show_type == ShowType.category:
            return self._show_cate_list(category, tags, order_type)
        else:
            return []

    def _show_monthly_recommend(self):
        article_ids = ACTION_SERVICE.retrieve_highest_click_article(number=30)

        result = []
        for article in ArticleStore.objects.filter(id__in=article_ids):
            article.concrete_article()
            result.append(article.to_dict(exclude=('publisher',)))

        return result

    def _show_interest_recommend(self, user_id):
        """
        1. 获取全体 热词(关键字) + 类目点击 + 分析点击发文 50%
        2. 获取单体 热词(关键字) + 类目点击 + 分析点击发文 50%

        3. 关键字60% 类目30% 标签10%
        """
        all_people_article_keywords, all_people_article_categories, all_people_article_tags = \
            ACTION_SERVICE.analyze_highest_click_article(number=10)
        my_article_keywords, my_article_categories, my_article_tags = \
            ACTION_SERVICE.analyze_highest_click_article(number=10, user_id=user_id)

        all_people_search_keywords = ACTION_SERVICE.retrieve_hot_word(number=10)
        my_search_keywords = ACTION_SERVICE.retrieve_hot_word(number=10, user_id=user_id)

        all_people_click_categories = ACTION_SERVICE.retrieve_highest_click_category(number=10)
        my_click_categories = ACTION_SERVICE.retrieve_highest_click_category(number=10, user_id=user_id)

        keywords = random_list_filter(all_people_search_keywords + my_search_keywords, number=5)
        categories = random_list_filter(all_people_click_categories + my_click_categories, number=2)
        tags = random_list_filter(all_people_article_tags + my_article_tags, number=2)

        return ARTICLE_INDEX_SERVICE.max_search(keyword=keywords, categories=categories, tags=tags)

    def _show_cate_list(self, category, tags, order_type):
        q = Q()
        if category and category > 0:
            # category只能单选查询
            category_leaves = CATEGORY_SERVICE.get_leaves(category_id=category)
            q |= Q(category__in=category_leaves)
        if tags:
            # tag可以多选查询
            for tag in tags:
                q |= Q(tags__contains=tag)

        result = []
        for article in ArticleStore.objects.filter(q).exclude(status=ArticleStore.DELETE_STATUS):
            article.concrete_article()
            result.append(article.to_dict(exclude=('publisher',)))

        result.reverse()

        return result

    @transaction.atomic
    def join_team(self, article_id, user):
        team_article = ArticleStore.objects.select_for_update().get(id=article_id)
        team_article.concrete_article()

        if not team_article.is_team_type():
            raise JoinTeamException(message='article({}) is not team article'.format(article_id))
        if team_article.content.get('total_number') <= team_article.content.get('now_number', 999):
            raise JoinTeamException(message='article({}) has full members'.format(article_id))
        if user.phone_number in [member.get('phone_number') for member in team_article.content.get('team_members')]:
            raise JoinTeamException(message='user({}) has been join article({})'.format(user.phone_number, article_id))

        team_article.content['now_number'] += 1
        team_member = user.to_dict(fields=('phone_number',))
        team_member.update({'is_leader': False})
        team_article.content.get('team_members', []).append(team_member)
        team_article.flat_article()

        # 表记录
        team_article.team_members.add(user)

        team_article.save()

        # 同步es，主要为了首页展示
        ARTICLE_INDEX_SERVICE.update_team_now_number(article_id=article_id, is_add=True)

        return team_article

    @transaction.atomic
    def leave_team(self, article_id, user):
        team_article = ArticleStore.objects.select_for_update().get(id=article_id)
        team_article.concrete_article()

        if not team_article.is_team_type():
            raise JoinTeamException(message='article({}) is not team article'.format(article_id))
        if not self.is_inside_team(team_article, user):
            raise JoinTeamException(message='user({}) not in article({})'.format(user.phone_number, article_id))

        team_article.content['now_number'] -= 1
        team_article.content['team_members'] = [member for member in team_article.content.get('team_members', []) if
                                                member.get('phone_number') != user.phone_number]
        team_article.flat_article()

        # 表记录
        team_article.team_members.remove(user)

        team_article.save()

        # 同步es，主要为了首页展示
        ARTICLE_INDEX_SERVICE.update_team_now_number(article_id=article_id, is_add=False)

        return team_article

    def is_inside_team(self, article, user):
        return bool(article.team_members.filter(id=user.id).first())

    def publish_recommend(self, article_id):
        """
        发布撮合
        1. 买租 《=》 卖租
        2. 组队
        """
        article = self.get_details(article_id)
        recommend_article_list = []

        rent_and_sale_category = [14, 16, 30]
        buy_and_hire_category = [15, 17, 30]
        play_and_study_team_category = [19, 31]
        car_team_category = [20, 31]

        if article.category_id in rent_and_sale_category:
            recommend_article_list.extend(ARTICLE_INDEX_SERVICE.min_search(keyword=article.abstract,
                                                                           categories=buy_and_hire_category))
        elif article.category_id in buy_and_hire_category:
            recommend_article_list.extend(ARTICLE_INDEX_SERVICE.min_search(keyword=article.abstract,
                                                                           categories=rent_and_sale_category))
        elif article.category_id in play_and_study_team_category:
            res = ARTICLE_INDEX_SERVICE.min_search(keyword=article.abstract, categories=play_and_study_team_category)
            recommend_article_list.extend([item for item in res if item.get('id') != article_id])
        elif article.category_id in car_team_category:
            # TODO 匹配地点和时间
            res = ARTICLE_INDEX_SERVICE.min_search(keyword=article.abstract, categories=car_team_category)
            recommend_article_list.extend([item for item in res if item.get('id') != article_id])
        else:
            pass
        return recommend_article_list

    def temp(self):
        for article in ArticleStore.objects.exclude(status=ArticleStore.DELETE_STATUS):
            article.concrete_article()
            article.abstract = jieba.analyse.extract_tags(
                "{},{},{}".format(article.title, article.content.get('body'), article.content.get('place', '')),
                topK=5)
            article.flat_article()
            article.save()
            ARTICLE_INDEX_SERVICE.publish(article)


class ArticleIndexService(object):
    """
    elastic search
    """

    doc_url = 'http://120.26.88.97:9200/article/_doc/{doc_id}'
    search_url = 'http://120.26.88.97:9200/article/_search'
    update_url = 'http://120.26.88.97:9200/article/_doc/{doc_id}/_update'

    def _write(self, article_id, data):
        if type(data) is not str:
            data = json.dumps(data)
        return requests.put(self.doc_url.format(doc_id=article_id), data=data,
                            headers={'Content-Type': 'application/json'})

    def _read(self, data):
        return requests.get(self.search_url, data=data, headers={'Content-Type': 'application/json'})

    def _update(self, article_id, data):
        if type(data) is not str:
            data = json.dumps(data)
        return requests.put(self.update_url.format(doc_id=article_id), data=data,
                            headers={'Content-Type': 'application/json'})

    def _delete(self, article_id):
        return requests.delete(self.doc_url.format(doc_id=article_id))

    def publish(self, article):
        if article.status == ArticleStore.DELETE_STATUS:
            return

        data = article.generate_es_put_data()
        res = self._write(article.id, data)

        # 错误处理
        if int(res.status_code / 100) != 2:
            article.status = ArticleStore.ES_ERROR_STATUS
            article.save()
        else:
            if article.status != ArticleStore.NORMAL_STATUS:
                article.status = ArticleStore.NORMAL_STATUS
                article.save()

        return res

    def delete(self, article_id):
        self._delete(article_id)

    def update(self, article):
        pass

    def update_view_time(self, article_id):
        data = {
            "script": "ctx._source.viewed_times+=1"
        }
        return self._update(article_id, data)

    def update_team_now_number(self, article_id, is_add=True):
        if is_add:
            data = {
                "script": "ctx._source.content.now_number+=1"
            }
        else:
            data = {
                "script": "ctx._source.content.now_number-=1"
            }
        return self._update(article_id, data)

    def max_search(self, keyword, *args, **kwargs):
        """
        宽松搜索， 关键字无须满足某类目下
        """
        categories = kwargs.get('categories', [])
        tags = kwargs.get('tags', [])

        # 请求es服务器
        if type(keyword) is str:
            keyword = keyword.split()
        search_dsl = self._get_max_search_dsl(keyword, categories, tags)
        res = self._read(search_dsl)
        res = json.loads(res.text)

        res_data_list = res.get('hits', {}).get('hits', [])
        return [self.format(res_data) for res_data in res_data_list]

    def min_search(self, keyword, *args, **kwargs):
        """
        严格搜索， 关键字必须满足某类目下
        """
        categories = kwargs.get('categories', [])
        tags = kwargs.get('tags', [])

        # 请求es服务器
        if type(keyword) is str:
            keyword = keyword.split()
        search_dsl = self._get_min_search_dsl(keyword, categories, tags)
        res = self._read(search_dsl)
        res = json.loads(res.text)

        res_data_list = res.get('hits', {}).get('hits', [])
        return [self.format(res_data) for res_data in res_data_list]

    @staticmethod
    def format(es_obj):
        obj_id = es_obj.get('_id')
        source = es_obj.get('_source', {})
        article = ArticleStore()
        article.id = obj_id
        article.title = source.get('title')
        article.content = source.get('content')
        article.pic_urls = source.get('pic_urls')
        article.tags = source.get('tags')
        article.publish_time = utc_to_datetime(source.get('publish_time'))
        article.publisher_id = source.get('publisher')
        article.category_id = source.get('category')
        article.viewed_times = source.get('viewed_times')
        article.report_level = source.get('report_level')
        article.abstract = source.get('abstract')

        return article.to_dict(exclude=('publisher',))

    @staticmethod
    def _get_max_search_dsl(keywords, categories=tuple(), tags=tuple()):
        if type(keywords) is not list and type(keywords) is not tuple:
            raise Exception()
        base_search_dsl = {
            "query": {
                "bool": {
                    "should": []
                }
            },
            "highlight": {
                "fields": {
                    "content.body": {},
                    "title": {},
                    "tags": {}
                },
                "pre_tags": "<123>",
                "post_tags": "</123>"
            }
        }
        for keyword in keywords:
            keywords_should_dsl_part = [
                {
                    "nested": {
                        "path": "content",
                        "query": {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase": {
                                            "content.body": {
                                                "query": keyword,
                                                "boost": 4
                                            }
                                        }
                                    },
                                    {
                                        "match_phrase": {
                                            "content.place": {
                                                "query": keyword,
                                                "boost": 4
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "match_phrase": {
                        "title": {
                            "query": keyword,
                            "boost": 4
                        }
                    }
                },
                {
                    "match_phrase": {
                        "tags.keyword": {
                            "query": keyword,
                            "boost": 4
                        }
                    }
                },
            ]
            base_search_dsl['query']['bool']['should'].extend(keywords_should_dsl_part)

        if type(tags) is list or type(tags) is tuple:
            tags = ','.join(tags)

        for tag in tags:
            tag_dsl_part = {
                "match": {
                    "tags": {
                        "query": tag,
                        "boost": 2
                    }
                }
            }
            base_search_dsl['query']['bool']['should'].append(tag_dsl_part)

        for category in categories:
            category_dsl_part = {
                "match": {
                    "category": {
                        "query": category,
                        "boost": 2
                    }
                }
            }
            base_search_dsl['query']['bool']['should'].append(category_dsl_part)
        return json.dumps(base_search_dsl)

    @staticmethod
    def _get_min_search_dsl(keywords, categories=tuple(), tags=tuple()):
        if type(keywords) is not list and type(keywords) is not tuple:
            raise Exception()
        base_search_dsl = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "highlight": {
                "fields": {
                    "content.body": {},
                    "title": {},
                    "tags": {}
                },
                "pre_tags": "<123>",
                "post_tags": "</123>"
            }
        }
        keywords_dsl_part = {
            "bool": {
                "should": []
            }
        }
        for keyword in keywords:
            keywords_should_dsl_part = [
                {
                    "nested": {
                        "path": "content",
                        "query": {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase": {
                                            "content.body": {
                                                "query": keyword,
                                                "boost": 4
                                            }
                                        }
                                    },
                                    {
                                        "match_phrase": {
                                            "content.place": {
                                                "query": keyword,
                                                "boost": 4
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "match_phrase": {
                        "title": {
                            "query": keyword,
                            "boost": 4
                        }
                    }
                },
                {
                    "match_phrase": {
                        "tags.keyword": {
                            "query": keyword,
                            "boost": 4
                        }
                    }
                },
            ]
            keywords_dsl_part['bool']['should'].extend(keywords_should_dsl_part)

        base_search_dsl['query']['bool']['must'].append(keywords_dsl_part)

        if type(tags) is list or type(tags) is tuple:
            tags = ','.join(tags)

        # tag
        tags_dsl_part = {
            "bool": {
                "should": []
            }
        }
        for tag in tags:
            tag_should_dsl_part = {
                "match": {
                    "tags": {
                        "query": tag,
                        "boost": 2
                    }
                }
            }
            tags_dsl_part['bool']['should'].append(tag_should_dsl_part)
        base_search_dsl['query']['bool']['must'].append(tags_dsl_part)

        # category
        categories_dsl_part = {
            "bool": {
                "should": []
            }
        }
        for category in categories:
            category_should_dsl_part = {
                "match": {
                    "category": {
                        "query": category,
                        "boost": 2
                    }
                }
            }
            categories_dsl_part['bool']['should'].append(category_should_dsl_part)
        base_search_dsl['query']['bool']['must'].append(categories_dsl_part)
        return json.dumps(base_search_dsl)

    def _backdoor_refresh_es_data(self, is_all=False):
        if is_all:
            for article in ArticleStore.objects.exclude(status=ArticleStore.DELETE_STATUS):
                self.publish(article)
        else:
            for article in ArticleStore.objects.filter(status=ArticleStore.ES_ERROR_STATUS):
                self.publish(article)


ARTICLE_SERVICE = ArticleService()
ARTICLE_INDEX_SERVICE = ArticleIndexService()
