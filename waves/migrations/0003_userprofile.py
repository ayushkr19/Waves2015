# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('waves', '0002_auto_20150617_2208'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, blank=True, to=settings.AUTH_USER_MODEL)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=50)),
                ('post', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('user_type', models.CharField(default=b'BA', max_length=5, choices=[(b'CM', b'Content Modifiers'), (b'EM', b'Event Managers'), (b'EH', b'Events Head'), (b'P', b'Participant'), (b'JU', b'Event Judge'), (b'BA', b'Basic Default User?')])),
                ('user_name_phone_num', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
