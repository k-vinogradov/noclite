# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0017_auto_20150709_1732'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='naconsolidationgroup',
            options={'ordering': ['name'], 'verbose_name': 'consolidation groups', 'verbose_name_plural': 'consolidation groups', 'permissions': (('view_cg', 'Can view accidents consolidation report'),)},
        ),
    ]
