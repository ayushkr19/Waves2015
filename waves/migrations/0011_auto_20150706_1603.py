# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0010_auto_20150702_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='subtitle',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
