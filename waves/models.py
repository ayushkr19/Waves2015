from django.contrib.auth.models import User
from django.db import models
from constants import *

# Create your models here.
# Post save signals in serializers.py
class Profile(models.Model):

    def __str__(self):
        return self.user.username + ", " + self.user.first_name + " " + self.user.last_name

    user = models.OneToOneField(User, null=True)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default=BASIC_USER, max_length=30)
    phone_num = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Event(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=50, unique=True)
    event_date = models.DateField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    description = models.TextField()
    event_url = models.URLField(blank=True, null=True)
    event_managers = models.ManyToManyField(Profile, blank=True, related_name='ems')


class Update(models.Model):
    def __str__(self):
        return self.heading + ',' + str(self.created_at)

    heading = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Profile, null=True)
    for_event = models.ForeignKey(Event, null=True)
    general_update = models.NullBooleanField()
    # tags? , Event Category?


