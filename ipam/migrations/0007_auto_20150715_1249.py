# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ipam.models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0006_vrf_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain4',
            name='last_updated',
            field=models.DateTimeField(default=ipam.models.datetime_now),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='expiry',
            field=models.CharField(default='2w', max_length=8, verbose_name='Expiry'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='nx',
            field=models.CharField(default='5m', max_length=8, verbose_name='NXDomain TTL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='refresh',
            field=models.CharField(default='20m', max_length=8, verbose_name='Refresh'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='retry',
            field=models.CharField(default='2m', max_length=8, verbose_name='Retry'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='sn',
            field=models.IntegerField(default=ipam.models.datetime_now_str, verbose_name='Serial number'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='soa_admin_mailbox',
            field=models.CharField(default='root.sibttk.net', max_length=255, verbose_name='Admin mailbox'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='soa_name_server',
            field=models.CharField(default='ns.sibttk.net', max_length=255, verbose_name='Name server'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain4',
            name='zone_type',
            field=models.CharField(default=b'in', max_length=4, verbose_name='Type', choices=[(b'in', b'IN')]),
            preserve_default=True,
        ),
    ]
