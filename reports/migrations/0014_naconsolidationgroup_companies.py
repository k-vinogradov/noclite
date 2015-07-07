# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0013_auto_20150706_0234'),
    ]

    operations = [
        migrations.AddField(
            model_name='naconsolidationgroup',
            name='companies',
            field=models.ManyToManyField(to='reports.NACompany', verbose_name='Companies'),
            preserve_default=True,
        ),
    ]
