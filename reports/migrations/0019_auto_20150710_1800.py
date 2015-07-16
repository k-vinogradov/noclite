# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0018_auto_20150709_1734'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nadaytype',
            options={'ordering': ['name'], 'verbose_name': 'type of a day', 'verbose_name_plural': 'types of a day'},
        ),
    ]
