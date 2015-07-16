# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0002_remove_domain4_last_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain4',
            name='last_ip',
            field=models.IPAddressField(default='80.240.36.255', verbose_name='Last IP address'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='c_hash',
            field=models.CharField(default=b'', max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
