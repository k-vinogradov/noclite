# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0015_naaccident_consolidation_report_ignore_cause'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='naconsolidationgroup',
            options={'ordering': ['name'], 'verbose_name': 'consolidation groups', 'verbose_name_plural': 'consolidation groups', 'permissions': ('view_cg', 'Can view accidents consolidation report')},
        ),
        migrations.AlterField(
            model_name='naaccident',
            name='consolidation_report_ignore_cause',
            field=models.TextField(default='', null=True, verbose_name='Cause of ignoring accident in the consolidation report', blank=True),
            preserve_default=True,
        ),
    ]
