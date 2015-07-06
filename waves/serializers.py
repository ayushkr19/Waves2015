from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from waves.models import Event, Profile
from rest_framework import serializers
from constants import *
from django.dispatch import receiver
from django.db.models.signals import post_save

def create_user(username, email, password, first_name, last_name):

    # TODO: Get user with the first_name, last_name, and email, and ensure duplicate entries do not exist?

    user = User.objects.create_user(username=username, email=email)
    if user:
        user.set_password(raw_password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    else:
        print('User None')
    return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password'
        )
        write_only_fields = ('password',)

    def create(self, validated_data):

        return create_user(username=validated_data['username'], email=validated_data['email'],
                           password=validated_data['password'], first_name=validated_data['first_name'],
                           last_name=validated_data['last_name'])

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    @receiver(post_save, sender=User)
    def add_to_groups_if_superuser(sender, instance, created, **kwargs):
        if instance.is_staff is True and instance.is_superuser is True:
            for group_name in ALL_GRPS_EXCEPT_ANONYMOUS_USER:
                group = Group.objects.get(name=group_name)
                instance.groups.add(group)

# Original Event serializer. Using the depth option
# returns additional unwanted data of the user objects.
# Thus the need of custom serializers
# class EventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Event
#         fields = ('name', 'subtitle', 'description', 'event_date', 'event_time',
#                   'event_url', 'created_at', 'modified_at', 'event_managers')
#         depth = 2


class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    user_type = serializers.CharField(default=BASIC_USER, max_length=30)
    phone_num = serializers.CharField(max_length=10)
    created_at = serializers.CharField(required=False)
    modified_at = serializers.CharField(required=False)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.get_or_create(**user_data)

        return Profile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')

        try:
            user = instance.user
        except ObjectDoesNotExist:
            user = User.objects.create_user(**user_data)

        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.phone_num = validated_data.get('phone_num', instance.phone_num)
        instance.save()

        user.email = user_data.get('email', user.email)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        password = user_data.get('password', None)
        if password:
            user.set_password(password)
        user.save()

        return instance


class EventSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    subtitle = serializers.CharField(max_length=50, default='')
    event_date = serializers.DateField(required=False)
    event_time = serializers.TimeField(required=False)
    created_at = serializers.DateTimeField(required=False)
    modified_at = serializers.DateTimeField(required=False)
    description = serializers.CharField()
    event_url = serializers.URLField(required=False)
    event_managers = ProfileSerializer(required=False, many=True)

    def create(self, validated_data):
        return Event.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update event objects.
        Event managers can't be updated from here.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.subtitle = validated_data.get('subtitle', instance.subtitle)
        instance.event_date = validated_data.get('event_date', instance.event_date)
        instance.event_time = validated_data.get('event_time', instance.event_time)
        instance.description = validated_data.get('description', instance.description)
        instance.event_url = validated_data.get('event_url', instance.event_url)
        instance.save()
        return instance


class AnyUserSerializer(serializers.Serializer):

    user = UserSerializer()
    user_type = serializers.CharField(default=BASIC_USER, max_length=30)
    phone_num = serializers.CharField(max_length=10)

    def create(self, validated_data):

        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.phone_num = validated_data.get('phone_num', instance.phone_num)
        instance.save()

        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        password = user_data.get('password', None)
        if password:
            user.set_password(password)
        user.save()

    @receiver(post_save, sender=Profile)
    def update_profile_user_groups(sender, instance, created, **kwargs):
        """
        Method to assign groups to users on the basis of their user type
        :param sender: Profile
        :param instance: The Profile instance
        :param created:
        :param kwargs:
        """

        user = instance.user
        user_type = instance.user_type

        group = Group.objects.get(name=user_type)
        user.groups.add(group)


