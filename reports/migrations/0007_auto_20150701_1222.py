# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20150701_1113'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='naaccident',
            name='Magistral customers affected',
        ),
        migrations.AddField(
            model_name='naaccident',
            name='magistral_customers_affected',
            field=models.BooleanField(default=False, verbose_name='Magistral customers affected'),
            preserve_default=True,
        ),
    ]
