from django.db import models


# Create your models here.
class BaseModel(models.Model):
    gmt_modified = models.DateTimeField('修改时间')
    gmt_created = models.DateTimeField('创建时间')


class GoodsModel(BaseModel):
    """
    商品信息
    """
    RENT = 'RENT'
    SELL = 'SELL'
    GOODS_OUT_CHOICES = (
        (RENT, 'RENT'),
        (SELL, 'SELL'),
    )

    OUT = 'OUT'
    IN = 'IN'
    GOODS_CHOICES = (
        (OUT, OUT),
        (IN, IN),
    )

    goods_name = models.CharField('商品名', max_length=1024)
    goods_tag = models.CharField('商品标签', max_length=1024)
    goods_category = models.CharField('商品所属类目', max_length=1024)

    goods_type = models.CharField('商品类型', choices=GOODS_CHOICES, default='default', max_length=64)
    goods_cover_pic_url = models.CharField('商品封面图', max_length=1024)

    goods_detail_info = models.CharField('详情说明', max_length=2048)
    goods_detail_pic_url = models.CharField('最多三张的详情说明图', max_length=1024)

    goods_publisher = models.IntegerField('发布人id', default=-1)
    goods_publish_time = models.DateTimeField('发布时间')
    goods_like_times = models.IntegerField('喜欢次数', default=0)
    goods_view_times = models.IntegerField('浏览次数', default=0)

    @staticmethod
    def get_goods_publisher(publisher_id):
        """
        获取发布者详细信息
        :param publisher_id: 发布者id
        :return: 用户信息
        """
        pass


# class TeamModel(BaseModel):
#     pass


# 用以区分goods和team
GOODS = 0
TEAM = 1
CASE_CHOICES = (
    (GOODS, 'goods'),
    (TEAM, 'team'),
)


class CommentStore(BaseModel):
    """
    评论系统
    """
    comment_type = models.IntegerField('评论类型', choices=CASE_CHOICES)
    comment_parents = models.IntegerField('评论回复上层id', default=0)
    comment_message = models.CharField('评论信息', max_length=1024)
    comment_publisher = models.IntegerField('发布人id', default=-1)

    @staticmethod
    def get_comment_publisher(publisher_id):
        """
        获取发布者详细信息
        :param publisher_id: 发布者id
        :return: 用户信息
        """
        pass


class UserViewRel(BaseModel):
    """
    浏览记录
    """
    user_view_type = models.IntegerField('浏览记录类型', choices=CASE_CHOICES)
    user_view_case_id = models.IntegerField('浏览记录id', default=-1)
    user_view_user_id = models.IntegerField('浏览者id', default=-1)


class UserLikeRel(BaseModel):
    """
    喜欢记录
    """
    user_like_type = models.IntegerField('喜欢记录类型', choices=CASE_CHOICES)
    user_like_case_id = models.IntegerField('喜欢记录id', default=-1)
    user_like_user_id = models.IntegerField('喜欢者id', default=-1)


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
