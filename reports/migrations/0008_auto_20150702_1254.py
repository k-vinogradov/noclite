# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_auto_20150701_1222'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='naaccident',
            options={'ordering': ['start_datetime', 'finish_datetime'], 'verbose_name': 'accident', 'verbose_name_plural': 'accidents', 'permissions': (('view', 'Can view network accidents'), ('view_na', 'Can view network accidents info'))},
        ),
        migrations.AddField(
            model_name='nacategory',
            name='color',
            field=models.CharField(default='default', max_length=8, verbose_name='Label color', choices=[(b'default', b'Default'), (b'primary', b'Primary'), (b'success', b'Success'), (b'info', b'Info'), (b'warning', b'Warning'), (b'danger', b'Danger')]),
            preserve_default=False,
        ),
    ]
