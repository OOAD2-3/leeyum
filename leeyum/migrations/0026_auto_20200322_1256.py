# Generated by Django 2.2.10 on 2020-03-22 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leeyum', '0025_categorystore_pic_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlestore',
            name='abstract',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='摘要'),
        ),
        migrations.AlterField(
            model_name='categorystore',
            name='pic_url',
            field=models.CharField(blank=True, default='http://leeyum-bucket.oss-cn-hangzhou.aliyuncs.com/category_pic/default.png', max_length=128, null=True, verbose_name='类目图片'),
        ),
    ]