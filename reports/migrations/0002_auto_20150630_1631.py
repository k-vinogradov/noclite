# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='najob',
            name='iss_id',
            field=models.IntegerField(null=True, verbose_name="ISS emergency job's number", blank=True),
            preserve_default=True,
        ),
    ]
