# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0007_auto_20150626_0156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_type',
            field=models.CharField(default=b'BasicUsers', max_length=30, choices=[(b'EventContentEditors', b'Content Modifiers'), (b'EventManagers', b'Event Managers'), (b'EventsHead', b'Events Head'), (b'Participant', b'Participant'), (b'Judges', b'Event Judge'), (b'BasicUsers', b'Basic Default User?')]),
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
