# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0014_naconsolidationgroup_companies'),
    ]

    operations = [
        migrations.AddField(
            model_name='naaccident',
            name='consolidation_report_ignore_cause',
            field=models.TextField(null=True, verbose_name='Cause of ignoring accident in the consolidation report', blank=True),
            preserve_default=True,
        ),
    ]
