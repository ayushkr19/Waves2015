# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0012_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='update',
            name='created_by',
            field=models.ForeignKey(to='waves.Profile', null=True),
        ),
        migrations.AlterField(
            model_name='update',
            name='for_event',
            field=models.ForeignKey(to='waves.Event', null=True),
        ),
    ]
