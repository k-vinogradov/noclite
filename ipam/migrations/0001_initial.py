# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain4',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zone', models.CharField(unique=True, max_length=255, verbose_name='Zone FQDN')),
                ('ttl', models.CharField(max_length=8, verbose_name='Time-to-Live')),
                ('zone_type', models.CharField(max_length=4, verbose_name='Type', choices=[(b'in', b'IN')])),
                ('soa_name_server', models.CharField(max_length=255, verbose_name='Name server')),
                ('soa_admin_mailbox', models.CharField(max_length=255, verbose_name='Admin mailbox')),
                ('sn', models.IntegerField(verbose_name='Serial number')),
                ('refresh', models.CharField(max_length=8, verbose_name='Refresh')),
                ('retry', models.CharField(max_length=8, verbose_name='Retry')),
                ('expiry', models.CharField(max_length=8, verbose_name='Expiry')),
                ('nx', models.CharField(max_length=8, verbose_name='NXDomain TTL')),
                ('name_servers', models.TextField(verbose_name='NS resource records')),
                ('first_ip', models.IPAddressField(verbose_name='First IP address')),
                ('last_ip', models.IPAddressField(verbose_name='Last IP address')),
                ('c_hash', models.CharField(default=b'', max_length=32, blank=True)),
            ],
            options={
                'verbose_name': 'domain',
                'verbose_name_plural': 'domains',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Prefix4',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(max_length=18, verbose_name='IP Address')),
                ('size', models.IntegerField(null=True, verbose_name='subnet size', blank=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('status', models.CharField(default='assigned', max_length=64, verbose_name='Status', choices=[('allocated', 'Allocated'), ('assigned', 'Assigned'), ('reserved', 'Reserved')])),
                ('domain', models.CharField(max_length=255, verbose_name='domain', blank=True)),
                ('host_name', models.CharField(max_length=255, verbose_name='host name', blank=True)),
                ('sequence_number', models.FloatField(null=True, blank=True)),
                ('first_ip_dec', models.IntegerField(null=True, blank=True)),
                ('last_ip_dec', models.IntegerField(null=True, blank=True)),
                ('parent', models.ForeignKey(related_name='child', on_delete=django.db.models.deletion.SET_NULL, verbose_name='parent', blank=True, to='ipam.Prefix4', null=True)),
            ],
            options={
                'ordering': ['sequence_number'],
                'verbose_name': 'IPv4 prefix',
                'verbose_name_plural': 'IPv4 Prefixes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vrf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(help_text='VRF name', unique=True, max_length=64, verbose_name='name')),
                ('rd', models.CharField(help_text='Route Distinguisher', unique=True, max_length=16, verbose_name='route-distinguisher')),
                ('description', models.TextField(verbose_name='description', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'VRF',
                'verbose_name_plural': 'VRFs',
                'permissions': (('view', 'Can view IPAM module content'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='prefix4',
            name='vrf',
            field=models.ForeignKey(related_name='prefixes_list', verbose_name='VRF', to='ipam.Vrf'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='prefix4',
            unique_together=set([('vrf', 'prefix')]),
        ),
        migrations.AddField(
            model_name='domain4',
            name='vrf',
            field=models.ForeignKey(verbose_name='VRF', to='ipam.Vrf'),
            preserve_default=True,
        ),
    ]
