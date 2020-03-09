# Generated by Django 2.2.10 on 2020-03-07 16:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leeyum', '0013_userstore_like_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentstore',
            name='comment_type',
        ),
        migrations.CreateModel(
            name='ReportStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gmt_modified', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('gmt_created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('report_reason', models.CharField(blank=True, max_length=1024, null=True, verbose_name='举报原因')),
                ('report_article', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='leeyum.ArticleStore')),
                ('report_comment', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='leeyum.CommentStore')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'leeyum_report',
            },
        ),
    ]
