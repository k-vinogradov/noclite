# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20150630_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='NARegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('cities', models.ManyToManyField(to='reports.NACity', verbose_name='Cities')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'verbose_name': 'region',
                'verbose_name_plural': 'regions',
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='naaccident',
            old_name='city',
            new_name='cities',
        ),
        migrations.RenameField(
            model_name='naaccident',
            old_name='company',
            new_name='companies',
        ),
        migrations.AddField(
            model_name='naday',
            name='region',
            field=models.ForeignKey(verbose_name='Region', blank=True, to='reports.NARegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nadaytype',
            name='region',
            field=models.ForeignKey(verbose_name='Region', blank=True, to='reports.NARegion', null=True),
            preserve_default=True,
        ),
    ]
