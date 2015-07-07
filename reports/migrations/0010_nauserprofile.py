# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0009_auto_20150703_0653'),
    ]

    operations = [
        migrations.CreateModel(
            name='NAUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accidents_list_started', models.DateTimeField(verbose_name='Start datetime for accidents list')),
                ('accidents_list_finished', models.DateTimeField(verbose_name='Finish datetime for accidents list')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
