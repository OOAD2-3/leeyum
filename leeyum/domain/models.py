import json
import copy

from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone

from leeyum.domain.utils import datetime_to_utc
from leeyum.infra.redis import REDIS_CLIENT


# Create your models here.
class BaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = ('id',)

    gmt_modified = models.DateTimeField('修改时间', auto_now=True)
    gmt_created = models.DateTimeField('创建时间', auto_now_add=True)

    def to_dict(self, fields=None, exclude=tuple()):
        data = {}
        for f in self._meta.concrete_fields + self._meta.many_to_many:
            value = f.value_from_object(self)

            if fields and f.name not in fields:
                continue

            if f.name in exclude + ('gmt_modified', 'gmt_created'):
                continue

            if isinstance(f, models.ManyToManyField):
                value = [item.to_dict() for item in getattr(self, f.name).all() if item]

            if isinstance(f, models.ForeignKey):
                value = getattr(self, f.name)
                if value:
                    value = value.to_dict()

            if isinstance(f, models.DateTimeField):
                # value = value.strftime('%Y-%m-%d %H:%M:%S') if value and getattr(value, 'strftime') else value
                value = value.strftime('%Y-%m-%d') if value and getattr(value, 'strftime') else value

            if isinstance(value, models.expressions.CombinedExpression):
                continue

            data[f.name] = value

        return data


class UserStore(AbstractUser, BaseModel):
    """
    继承AbstractUser抽象类
    用户信息表
    """

    class Meta:
        db_table = "auth_user"

    phone_number = models.CharField('电话', max_length=11, null=True, blank=False)
    profile_avatar_url = models.CharField('头像', max_length=256, null=True, blank=True)
    like_article = models.ManyToManyField('ArticleStore')

    def __str__(self):
        return '{} {}'.format(self.username, self.phone_number)

    @staticmethod
    def check_captcha(phone_number, captcha):
        """
        验证传入短信验证码是否正确
        """
        redis_value = REDIS_CLIENT.get_object(phone_number)
        return redis_value == captcha


# class UserViewRel(BaseModel):
#     """
#     浏览记录
#     """
#     user_view_case_id = models.IntegerField('浏览记录id', default=-1)
#     user_view_user_id = models.IntegerField('浏览者id', default=-1)
#
#


class TagStore(BaseModel):
    """
    标签
    """

    class Meta:
        db_table = "leeyum_tag"

    name = models.CharField('标签名字', max_length=128, null=True, blank=False)
    intro = models.CharField('标签介绍', max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class CategoryStore(BaseModel):
    """
    类目
    """

    class Meta:
        db_table = "leeyum_category"

    name = models.CharField('类目名字', max_length=128, null=True, blank=False)
    intro = models.CharField('类目介绍', max_length=256, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='sub_category', null=True, blank=True,
                               default=-1)

    def __str__(self):
        return self.name


class ArticleStore(BaseModel):
    """
    信息模块
    """
    NORMAL_STATUS = 0
    DELETE_STATUS = -1
    ES_ERROR_STATUS = 2

    # 举报等级
    NORMAL = 3
    PROBLEM = 4
    DANGER = 5

    content_fields = ['body',
                      'price', 'new_or_old', 'time_span',
                      'time', 'place', 'total_number',
                      'time', 'place', 'price', 'target_grade', 'sex_require']

    full_content_fields_intro = {
        'body': '详情',
        'price': '价格',
        'new_or_old': '崭新程度',
        'time_span': '租售时长',
        'time': '时间',
        'place': '地点',
        'total_number': '总人数',
        'now_number': '当前人数',
        'team_members': '队伍成员信息'
    }

    class Meta:
        db_table = "leeyum_article"

    title = models.CharField('标题', max_length=1024, null=True, blank=False)
    pic_urls = models.CharField('图片url', max_length=2048, null=True, blank=False)
    content = models.CharField('详情内容', max_length=1024 * 10, null=True, blank=True)
    viewed_times = models.IntegerField('浏览次数', null=True, blank=True, default=0)

    tags = models.CharField('标签 拍平存储', max_length=1024, null=True, blank=True)
    category = models.ForeignKey(CategoryStore, on_delete=models.DO_NOTHING, default=-1)
    publisher = models.ForeignKey(UserStore, on_delete=models.DO_NOTHING, default=-1)
    publish_time = models.DateTimeField("发布时间", default=timezone.now)

    report_level = models.IntegerField('举报等级', default=NORMAL)

    # 非es字段
    status = models.IntegerField('状态', default=NORMAL_STATUS)

    def __str__(self):
        return self.title

    def format_content(self, content_details, **kwargs):
        """
        将dict => str，并增删必要参数
        """
        format_dict = {}
        for field in set(self.content_fields):
            if content_details.get(field):
                # 发布为组队信息，冗余队长信息，初始化队员信息
                if field == 'total_number':
                    leader = self.publisher.to_dict(fields=('phone_number',))
                    leader.update({'is_leader': True})
                    format_dict['team_members'] = [leader]
                    format_dict['now_number'] = 1
                    content_details[field] = int(content_details.get(field))

                format_dict[field] = content_details.get(field)

        return json.dumps(format_dict)

    def get_content_field_intro(self, field_name):
        return self.full_content_fields_intro.get(field_name, 'unexpect field')

    def concrete_article(self):
        """
        具象化被拍平的字段
        例如: '["www.baidu.com"]' ==> ["www.baidu.com"], str => list
        """
        self.pic_urls = json.loads(self.pic_urls) if type(self.pic_urls) is str else self.pic_urls
        self.content = json.loads(self.content) if type(self.content) is str else self.content
        self.tags = json.loads(self.tags) if type(self.tags) is str else self.tags
        return self

    def flat_article(self):
        """
        拍平字段 与concrete article作用相反
        """
        self.pic_urls = json.dumps(self.pic_urls) if type(self.pic_urls) is not str else self.pic_urls
        self.content = json.dumps(self.content) if type(self.content) is not str else self.content
        self.tags = json.dumps(self.tags) if type(self.tags) is not str else self.tags
        return self

    def to_dict(self, fields=None, exclude=tuple()):
        result = BaseModel.to_dict(self, fields, exclude)
        category = result.get('category', {})
        category_format_list = []
        while category is not None:
            category_format_list.append(category.get('name'))
            category = category.get('parent')

        category_format_list.reverse()
        result['category'] = category_format_list
        return result

    def generate_es_put_data(self):
        # 具象化被拍平的字段
        copy_article = copy.copy(self)
        copy_article.concrete_article()
        return {
            "title": copy_article.title,
            "pic_urls": copy_article.pic_urls,
            "content": copy_article.content,
            "tags": copy_article.tags,
            "publish_time": datetime_to_utc(copy_article.publish_time),
            "publisher": copy_article.publisher_id,
            "category": copy_article.category_id
        }

    def is_team_type(self):
        if type(self.content) is str:
            return 'total_number' in self.content
        else:
            return self.content.get('total_number') is not None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        重写save函数，一定先拍平才能存储
        """
        self.flat_article()
        return super().save(force_insert=False, force_update=False, using=None,
                            update_fields=None)


class CommentStore(BaseModel):
    """
    评论系统
    """
    NORMAL = 3
    PROBLEM = 4
    DANGER = 5

    class Meta:
        db_table = "leeyum_comment"

    comment_parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='sub_comment', null=True,
                                       blank=True, default=-1)
    comment_message = models.CharField('评论信息', max_length=1024, null=True, blank=True)

    comment_publisher = models.ForeignKey(UserStore, on_delete=models.DO_NOTHING)
    comment_article = models.ForeignKey(ArticleStore, on_delete=models.DO_NOTHING)

    report_level = models.IntegerField('举报等级', default=NORMAL)

    def __str__(self):
        return self.comment_message


class ReportStore(BaseModel):
    """
    举报系统
    """

    class Meta:
        db_table = "leeyum_report"

    report_article = models.ForeignKey(ArticleStore, on_delete=models.DO_NOTHING, null=True, blank=True)
    report_comment = models.ForeignKey(CommentStore, on_delete=models.DO_NOTHING, null=True, blank=True)
    report_reason = models.CharField('举报原因', max_length=1024, null=True, blank=True)
    reporter = models.ForeignKey(UserStore, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}_{}'.format(self.report_article, self.report_reason)


class FileUploadRecorder(BaseModel):
    """
    文件上传记录，主要为图片
    """

    class Meta:
        db_table = "leeyum_file_upload"

    file_name = models.CharField('上传文件名', max_length=1024, null=True, blank=True)
    file_url = models.CharField('上传文件url', max_length=1024, null=True, blank=True)
    is_used = models.BooleanField('使用状态', default=False)

    @staticmethod
    def use_these_files(file_urls):
        file_recorder_list = FileUploadRecorder.objects.filter(file_url__in=file_urls).update(is_used=True)
        return file_recorder_list

    @staticmethod
    def abandon_these_files(file_urls):
        file_recorder_list = FileUploadRecorder.objects.filter(file_url__in=file_urls).update(is_used=False)
        return file_recorder_list


class ActionDefinition(BaseModel):
    """
    动作定义表
    """

    class Meta:
        db_table = "leeyum_action_definition"
        unique_together = ('action_type', 'record_data', 'user')

    USER_BEHAVIOUR = 1
    SYSTEM_RECODER = 2

    action_type = models.CharField('动作名', max_length=128, null=True, blank=True)
    record_data = models.CharField('记录值', max_length=128, null=True, blank=True)
    user = models.ForeignKey(UserStore, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}_{}'.format(self.action_type, self.record_data)


class ActionTimeRecorder(BaseModel):
    """
    动作记录表
    """

    class Meta:
        db_table = "leeyum_action_time_recorder"
        unique_together = ('action_definition', 'record_date')

    action_definition = models.ForeignKey(ActionDefinition, on_delete=models.DO_NOTHING, related_name='actions')
    day_count = models.IntegerField('天记录值', null=True, blank=True, default=0)
    week_count = models.IntegerField('周记录值（7天）', null=True, blank=True, default=0)
    month_count = models.IntegerField('月记录值（30天）', null=True, blank=True, default=0)
    total_count = models.IntegerField('总记录', null=True, blank=True, default=0)

    week_ttl = models.IntegerField('周倒计时', default=1)
    month_ttl = models.IntegerField('月倒计时', default=1)

    record_date = models.DateField('记录时间', auto_now_add=True)
