# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0008_auto_20150627_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_managers',
            field=models.ManyToManyField(related_name='ems', null=True, to='waves.Profile', blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_type',
            field=models.CharField(default=b'BasicUsers', max_length=30, choices=[(b'EventContentEditors', b'Content Modifiers'), (b'EventManagers', b'Event Managers'), (b'EventsHead', b'Events Head'), (b'Participant', b'Participant'), (b'Judges', b'Event Judge'), (b'BasicUsers', b'Basic Default User'), (b'CoCo', b'COCO'), (b'Developers', b'Developers')]),
        ),
    ]
