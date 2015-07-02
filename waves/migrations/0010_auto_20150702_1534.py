# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0009_auto_20150702_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_managers',
            field=models.ManyToManyField(related_name='ems', to='waves.Profile', blank=True),
        ),
    ]
