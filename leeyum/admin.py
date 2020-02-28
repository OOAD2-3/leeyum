import json

from django.contrib import admin
from django.utils.safestring import mark_safe

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

    list_display = ('id', 'title', 'pic_urls', 'content', 'tags', 'category', 'publisher', 'publish_time')

    # filter_horizontal = ('tags',)

    # 自定义字段 - 图片预览
    def image_shows(self, obj):
        image = obj.pic_urls
        if image:
            image_html = ""
            for img_url in json.loads(image):
                artwork = ".".join(img_url.split(".")[0:-2])
                # 根据业务需求, 拿到所有图片的url, 拼接 img 及 a 标签
                image_html += '<a href="{}" target="_blank"><img src="{}" style="width:200px; height:200px; margin-right:2.5px; margin-left:2.5px; margin-bottom:5px"/></a>'.format(
                    artwork, img_url)
            html = "<div>" + image_html + "</div><div>提示: 点击图片查看原图</div>"
        else:
            html = "-"
        return mark_safe(html)  # 取消转义

    def content_shows(self, obj):
        try:
            content = json.loads(obj.content)
            if content:
                content_body = content.get('body', '')
                html = '<div>详情(body): ' + content_body + '</div>'
            else:
                html = '-'
        except Exception as e:
            html = '<div>content 存储结构存在问题，<a href="www.json.cn" target="_blank">请检查</a></div><div>{}</div>'.format(obj.content)

        return mark_safe(html)

    content_shows.allow_tags = True
    content_shows.short_description = '详情预览'

    image_shows.short_description = "图片预览"
    image_shows.allow_tags = True

    # 自定义字段 -

    # 重写编辑页, 继承父类方法
    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.fields = ('title', 'pic_urls', 'image_shows', 'content', 'content_shows',
                       'tags', 'category', 'publisher', 'publish_time')
        self.readonly_fields = ('image_shows', 'content_shows')
        return super().change_view(request, object_id, form_url='', extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        self.fields = ('title', 'pic_urls', 'content', 'tags', 'category', 'publisher', 'publish_time')
        return super().add_view(request, form_url='', extra_context=None)

    def save_model(self, request, obj, form, change):
        self.message_user(request, 'hello 测试一下')
        # super().save_model(request, obj, form, change)
        # ARTICLE_INDEX_SERVICE.publish(obj)


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
