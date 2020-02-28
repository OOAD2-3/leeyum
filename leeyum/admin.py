from django.contrib import admin
from leeyum.domain import models
from leeyum.domain.service.article import ARTICLE_INDEX_SERVICE

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

    list_display = ('id', 'title', 'pic_urls', 'content', 'tags', 'category', 'publish_time')
    # filter_horizontal = ('tags',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ARTICLE_INDEX_SERVICE.publish(obj)


@admin.register(models.CommentStore)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TagStore)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'intro')


@admin.register(models.CategoryStore)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'intro', 'parent')
    list_filter = ('parent',)
    ordering = ('-parent',)


@admin.register(models.UserStore)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'email', 'is_superuser', 'last_login')
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'phone_number', 'password', 'email', 'profile_avatar_url',),
            }),
        ('高级信息', {
            'classes': ('collapse',),  # 把‘高级信息’默认折叠起来
            'fields': (('is_superuser', 'is_staff', 'is_active'),),
        })
    )
