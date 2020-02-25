import json

from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone

from leeyum.infra.redis import REDIS_CLIENT


class ObjectStatus(object):
    normal = 0
    deleted = -1


# Create your models here.
class BaseModel(models.Model):
    class Meta:
        abstract = True

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
                value = value.strftime('%Y-%m-%d %H:%M:%S') if value and getattr(value, 'strftime') else value

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

    def __str__(self):
        return '{} {}'.format(self.username, self.phone_number)

    @staticmethod
    def check_captcha(phone_number, captcha):
        """
        验证传入短信验证码是否正确
        todo 验证码记得处理
        """
        redis_value = REDIS_CLIENT.get_object(phone_number)
        # return redis_value == captcha
        return True


# class UserViewRel(BaseModel):
#     """
#     浏览记录
#     """
#     user_view_case_id = models.IntegerField('浏览记录id', default=-1)
#     user_view_user_id = models.IntegerField('浏览者id', default=-1)
#
#
# class UserLikeRel(BaseModel):
#     """
#     喜欢记录
#     """
#     user_like_case_id = models.IntegerField('喜欢记录id', default=-1)
#     user_like_user_id = models.IntegerField('喜欢者id', default=-1)


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
    # parent = models.IntegerField('上级id', default=0)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='sub_category', null=True, blank=True, default=-1)

    def __str__(self):
        return self.name


class ArticleStore(BaseModel):
    """
    信息模块
    """

    class Meta:
        db_table = "leeyum_article"

    title = models.CharField('标题', max_length=1024, null=True, blank=False)
    pic_urls = models.CharField('图片url', max_length=2048, null=True, blank=False)
    content = models.CharField('详情内容', max_length=1024, null=True, blank=True)

    tags = models.CharField('标签 拍平存储', max_length=1024, null=True, blank=True)
    category = models.ForeignKey(CategoryStore, on_delete=models.DO_NOTHING, default=-1)
    publisher = models.ForeignKey(UserStore, on_delete=models.DO_NOTHING, default=-1)
    publish_time = models.DateTimeField("发布时间", default=timezone.now)

    def __str__(self):
        return self.title

    @staticmethod
    def format_content(body):
        format_dict = {
            'body': body
        }
        return json.dumps(format_dict)

    def concrete_article(self):
        self.pic_urls = json.loads(self.pic_urls)
        self.content = json.loads(self.content)
        self.tags = json.loads(self.tags)

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


class CommentStore(BaseModel):
    """
    评论系统
    """

    class Meta:
        db_table = "leeyum_comment"

    comment_parents = models.IntegerField('评论回复上层id', default=0)
    comment_message = models.CharField('评论信息', max_length=1024, null=True, blank=True)

    comment_publisher = models.ForeignKey(UserStore, on_delete=models.DO_NOTHING)
    comment_article = models.ForeignKey(ArticleStore, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.comment_message


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
        file_recorder_list = FileUploadRecorder.objects.filter(file_url__in=file_urls)
        for file_recorder in file_recorder_list:
            if file_recorder is None:
                continue

            file_recorder.is_used = True
            file_recorder.save()
        return file_recorder_list

    @staticmethod
    def abandon_these_files(file_urls):
        file_recorder_list = FileUploadRecorder.objects.filter(file_url__in=file_urls)
        for file_recorder in file_recorder_list:
            if file_recorder is None:
                continue

            file_recorder.is_used = False
            file_recorder.save()
        return file_recorder_list
