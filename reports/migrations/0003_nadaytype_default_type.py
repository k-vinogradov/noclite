# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20150630_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='nadaytype',
            name='default_type',
            field=models.BooleanField(default=False, verbose_name='Default type of day'),
            preserve_default=True,
        ),
    ]
