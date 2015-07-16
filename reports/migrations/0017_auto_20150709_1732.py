# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0016_auto_20150709_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='naaccident',
            name='consolidation_report_ignore_cause',
            field=models.TextField(default='', verbose_name='Cause of ignoring accident in the consolidation report', blank=True),
            preserve_default=True,
        ),
    ]
