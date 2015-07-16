# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0003_auto_20150710_1901'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domain4',
            old_name='c_hash',
            new_name='control_hash',
        ),
        migrations.AddField(
            model_name='domain4',
            name='slug',
            field=models.SlugField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
