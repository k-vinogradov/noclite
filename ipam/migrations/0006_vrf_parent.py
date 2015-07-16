# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0005_remove_domain4_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='vrf',
            name='parent',
            field=models.ForeignKey(verbose_name='Parent VRF', blank=True, to='ipam.Vrf', null=True),
            preserve_default=True,
        ),
    ]
