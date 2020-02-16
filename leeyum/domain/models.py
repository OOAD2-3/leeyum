from django.db import models


class ObjectStatus(object):
    normal = 0
    deleted = -1


# Create your models here.
class BaseModel(models.Model):
    class Meta:
        abstract = True

    gmt_modified = models.DateTimeField('修改时间')
    gmt_created = models.DateTimeField('创建时间')


class UserStore(BaseModel):
    class Meta:
        db_table = "leeyum_user"

    pass


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

    name = models.CharField('标签名字', max_length=128)
    intro = models.CharField('标签介绍', max_length=256)

    def __str__(self):
        return self.name


class CategoryStore(BaseModel):
    """
    类目
    """
    class Meta:
        db_table = "leeyum_category"

    name = models.CharField('类目名字', max_length=128)
    intro = models.CharField('类目介绍', max_length=256)
    parent = models.IntegerField('上级id', default=0)

    def __str__(self):
        return self.name


class ArticleStore(BaseModel):
    """
    信息模块
    """
    class Meta:
        db_table = "leeyum_article"

    title = models.CharField('标题', max_length=1024)
    pic_urls = models.CharField('图片url', max_length=2048)
    content = models.CharField('详情内容', max_length=1024)

    tags = models.ManyToManyField(TagStore)
    category = models.ForeignKey(CategoryStore, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class CommentStore(BaseModel):
    """
    评论系统
    """
    class Meta:
        db_table = "leeyum_comment"

    comment_parents = models.IntegerField('评论回复上层id', default=0)
    comment_message = models.CharField('评论信息', max_length=1024)

    comment_publisher = models.ForeignKey(UserStore, on_delete=models.CASCADE)
    comment_article = models.ForeignKey(ArticleStore, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_message
