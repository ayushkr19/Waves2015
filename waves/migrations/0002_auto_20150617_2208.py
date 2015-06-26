# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_time',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='subtitle',
            field=models.CharField(default=b'', max_length=50, blank=True),
        ),
    ]
