from django.contrib import admin
from leeyum.domain import models

admin.site.site_header = '流云校园'
admin.site.site_title = '流云校园管理后台'


@admin.register(models.ArticleStore)
class ArticleAdmin(admin.ModelAdmin):
    # list_display 设置要显示在列表中的字段（id字段是Django模型的默认主键）
    # list_per_page 设置每页显示多少条记录，默认是100条
    # ordering 设置默认排序字段，负号表示降序排序
    # list_editable 设置默认可编辑字段
    # fk_fields 设置显示外键字段
    # list_display_links 设置哪些字段可以点击进入编辑界面
    # list_filter 筛选器
    # search_fields 搜索器
    @staticmethod
    def tags(obj):
        return [item.name for item in obj.tags.all()]

    list_display = ('id', 'title', 'pic_urls', 'content', 'tags', 'category')
    filter_horizontal = ('tags',)


@admin.register(models.CommentStore)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TagStore)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CategoryStore)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserStore)
class UserAdmin(admin.ModelAdmin):
    pass
