# Generated by Django 2.2.10 on 2020-03-22 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leeyum', '0026_auto_20200322_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlestore',
            name='abstract',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='摘要'),
        ),
    ]