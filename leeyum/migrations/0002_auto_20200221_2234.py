# Generated by Django 2.2.10 on 2020-02-21 22:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leeyum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorystore',
            name='parent',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sub_category', to='leeyum.CategoryStore'),
        ),
    ]