# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20150630_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='NAAccident',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_datetime', models.DateTimeField(null=True, verbose_name='Time of the beginning', blank=True)),
                ('finish_datetime', models.DateTimeField(null=True, verbose_name='Time of the finishing', blank=True)),
                ('locations', models.TextField(null=True, verbose_name='Locations', blank=True)),
                ('affected_customers', models.IntegerField(null=True, verbose_name='Number of affected customers', blank=True)),
                ('Magistral customers affected', models.BooleanField(default=False)),
                ('reason', models.TextField(null=True, verbose_name='Cause of accident', blank=True)),
                ('actions', models.TextField(null=True, verbose_name='Emergency actions', blank=True)),
                ('iss_id', models.IntegerField(null=True, verbose_name="ISS emergency job's number", blank=True)),
                ('category', models.ForeignKey(verbose_name='Category', blank=True, to='reports.NACategory', null=True)),
                ('city', models.ManyToManyField(to='reports.NACity', null=True, verbose_name='City', blank=True)),
                ('company', models.ManyToManyField(to='reports.NACompany', null=True, verbose_name='Company', blank=True)),
                ('kind', models.ForeignKey(verbose_name='Kind', blank=True, to='reports.NAKind', null=True)),
            ],
            options={
                'ordering': ['start_datetime', 'finish_datetime'],
                'verbose_name': 'accident',
                'verbose_name_plural': 'accidents',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='najob',
            name='category',
        ),
        migrations.RemoveField(
            model_name='najob',
            name='city',
        ),
        migrations.RemoveField(
            model_name='najob',
            name='company',
        ),
        migrations.RemoveField(
            model_name='najob',
            name='kind',
        ),
        migrations.DeleteModel(
            name='NAJob',
        ),
    ]
