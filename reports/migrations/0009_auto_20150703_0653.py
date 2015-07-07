# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_auto_20150702_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='NATimeLimit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main_limit', models.IntegerField(verbose_name='Time limit (min)')),
                ('magistral_affected_limit', models.IntegerField(verbose_name='Schedule if magistral customers was affected (min)')),
                ('category', models.ForeignKey(verbose_name='Category of accident', to='reports.NACategory')),
                ('kind', models.ForeignKey(verbose_name='Kind of accident', to='reports.NAKind')),
            ],
            options={
                'ordering': ['category', 'kind'],
                'verbose_name': 'time limit',
                'verbose_name_plural': 'time limits',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='natimelimits',
            name='category',
        ),
        migrations.RemoveField(
            model_name='natimelimits',
            name='kind',
        ),
        migrations.DeleteModel(
            name='NATimeLimits',
        ),
    ]
