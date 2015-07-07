# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0010_nauserprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='NAConsolidationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('regions', models.ManyToManyField(to='reports.NARegion', verbose_name='Regions for consolidation')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'verbose_name': 'consolidation groups',
                'verbose_name_plural': 'consolidation groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NAKindCategoryMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('categories', models.ManyToManyField(to='reports.NACategory', verbose_name='Categories')),
                ('consolidation_group', models.ForeignKey(to='reports.NAConsolidationGroup')),
                ('kinds', models.ManyToManyField(to='reports.NAKind', verbose_name='Kinds of accidents')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
