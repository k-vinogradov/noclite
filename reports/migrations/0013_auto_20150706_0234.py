# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0012_auto_20150706_0230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='natimelimit',
            name='kind',
            field=models.ForeignKey(verbose_name='Kind of accident', blank=True, to='reports.NAKind', null=True),
            preserve_default=True,
        ),
    ]
