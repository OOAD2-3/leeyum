# Generated by Django 2.2.10 on 2020-03-13 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leeyum', '0020_auto_20200311_2238'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='actiondefinition',
            unique_together={('action_type', 'record_data', 'user')},
        ),
    ]