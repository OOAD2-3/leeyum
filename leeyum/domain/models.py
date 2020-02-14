from django.db import models


# Create your models here.
class BaseModel(models.Model):
    gmt_modified = models.DateTimeField('修改时间')
    gmt_created = models.DateTimeField('创建时间')


class ArticleStore(BaseModel):
    """
    信息模块
    """
    pass


class CommentStore(BaseModel):
    """
    评论系统
    """
    comment_parents = models.IntegerField('评论回复上层id', default=0)
    comment_message = models.CharField('评论信息', max_length=1024)
    comment_publisher = models.IntegerField('发布人id', default=-1)


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
    name = models.CharField('标签名字', max_length=128)
    intro = models.CharField('标签介绍', max_length=256)


class CategoryStore(BaseModel):
    """
    类目
    """
    name = models.CharField('类目名字', max_length=128)
    intro = models.CharField('类目介绍', max_length=256)
    parent = models.IntegerField('上级id', default=0)


# class UserStore(BaseModel):
#     pass
