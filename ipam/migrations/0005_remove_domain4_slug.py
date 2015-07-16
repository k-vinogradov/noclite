# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0004_auto_20150710_1915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain4',
            name='slug',
        ),
    ]
