# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NACategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('number', models.IntegerField(unique=True, verbose_name='Number')),
                ('title', models.CharField(max_length=4, verbose_name='Caption')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ['number'],
                'abstract': False,
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NACity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NACompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'verbose_name': 'company',
                'verbose_name_plural': 'companies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NADay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='Date')),
            ],
            options={
                'ordering': ['date'],
                'verbose_name': 'day',
                'verbose_name_plural': 'days',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NADayType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('start', models.TimeField(verbose_name='Start')),
                ('finish', models.TimeField(verbose_name='Finish')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'verbose_name': 'type of day',
                'verbose_name_plural': 'types of day',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NAJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_datetime', models.DateTimeField(null=True, verbose_name='Time of the beginning', blank=True)),
                ('finish_datetime', models.DateTimeField(null=True, verbose_name='Time of the finishing', blank=True)),
                ('locations', models.TextField(null=True, verbose_name='Locations', blank=True)),
                ('affected_customers', models.IntegerField(null=True, verbose_name='Number of affected customers', blank=True)),
                ('Magistral customers affected', models.BooleanField(default=False)),
                ('reason', models.TextField(null=True, verbose_name='Cause of accident', blank=True)),
                ('actions', models.TextField(null=True, verbose_name='Emergency actions', blank=True)),
                ('iss_id', models.IntegerField(verbose_name="ISS emergency job's number", blank=True)),
                ('category', models.ForeignKey(verbose_name='Category', blank=True, to='reports.NACategory', null=True)),
                ('city', models.ManyToManyField(to='reports.NACity', null=True, verbose_name='City', blank=True)),
                ('company', models.ManyToManyField(to='reports.NACompany', null=True, verbose_name='Company', blank=True)),
            ],
            options={
                'ordering': ['start_datetime', 'finish_datetime'],
                'verbose_name': 'accident',
                'verbose_name_plural': 'accidents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NAKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('code', models.CharField(unique=True, max_length=8, verbose_name='Code')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ['code', 'title'],
                'verbose_name': 'kind of accident',
                'verbose_name_plural': 'kinds of accident',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NATimeLimits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main_limit', models.IntegerField(verbose_name='Time limit (min)')),
                ('magistral_affected_limit', models.IntegerField(verbose_name='Schedule if magistral customers was affected (min)')),
                ('category', models.ForeignKey(verbose_name='Category of accident', to='reports.NACategory')),
                ('kind', models.ForeignKey(verbose_name='Kind of accident', to='reports.NAKind')),
            ],
            options={
                'ordering': ['category', 'kind'],
                'verbose_name': 'time limit',
                'verbose_name_plural': 'time limits',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NAWorkHours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main_schedule', models.CharField(max_length=4, verbose_name='Schedule', choices=[(b'WH', 'During the working hours'), (b'24', 'Around the Clock')])),
                ('magistral_affected_schedule', models.CharField(max_length=4, verbose_name='Schedule if magistral customers was affected', choices=[(b'WH', 'During the working hours'), (b'24', 'Around the Clock')])),
                ('category', models.ForeignKey(verbose_name='Category of accident', to='reports.NACategory')),
                ('kind', models.ForeignKey(verbose_name='Kind of accident', to='reports.NAKind')),
            ],
            options={
                'ordering': ['kind', 'category'],
                'verbose_name': 'schedule',
                'verbose_name_plural': 'schedules',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='najob',
            name='kind',
            field=models.ForeignKey(verbose_name='Kind', blank=True, to='reports.NAKind', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='naday',
            name='day_type',
            field=models.ForeignKey(verbose_name='Type of day', to='reports.NADayType'),
            preserve_default=True,
        ),
    ]
