# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_nadaytype_default_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nadaytype',
            name='default_type',
        ),
        migrations.AddField(
            model_name='nadaytype',
            name='default_day_off',
            field=models.BooleanField(default=False, verbose_name='Default day off'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nadaytype',
            name='default_workday',
            field=models.BooleanField(default=False, verbose_name='Default workday'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='nadaytype',
            name='finish',
            field=models.TimeField(null=True, verbose_name='Finish', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='nadaytype',
            name='start',
            field=models.TimeField(null=True, verbose_name='Start', blank=True),
            preserve_default=True,
        ),
    ]
