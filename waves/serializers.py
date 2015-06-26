from django.contrib.auth.models import User, Group
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
        # TODO: Remove
        print('User None')
    return user


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('name', 'subtitle', 'description', 'event_date', 'event_time',
                  'event_url', 'created_at', 'modified_at')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password'
        )
        write_only_fields = ('password',)

    def create(self, validated_data):

        print('\n Creating user. (in create() of UserSerializer)')

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


class AnyUserSerializer(serializers.Serializer):

    user = UserSerializer()
    user_type = serializers.CharField(default=BASIC_USER, max_length=5)
    phone_num = serializers.CharField(max_length=10)

    def create(self, validated_data):

        print('\n In create() of AnyUserSerializer')
        print('\n Printing validated data :')
        print(validated_data)

        user_data = validated_data.pop('user')

        print('\n Printing user data:')
        print(user_data)

        user = User.objects.create_user(**user_data)

        print('\nPrinting user object')
        print(user)

        profile = Profile.objects.create(user=user, **validated_data)

        print('\n Printing profile object: ')
        print(profile)

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
        print('In post save')
        user = instance.user
        print(user)

        user_type = instance.user_type
        print(user_type)

        if user_type == CONTENT_MODIFIERS:
            group = Group.objects.get(name=CONTENT_MODIFIERS_GRP)
            user.groups.add(group)
        elif user_type == EVENT_MANAGERS:
            group = Group.objects.get(name=EVENT_MANAGERS_GRP)
            user.groups.add(group)
        elif user_type == PARTICIPANT:
            group = Group.objects.get(name=PARTICIPANT_GRP)
            user.groups.add(group)
        elif user_type == BASIC_USER:
            group = Group.objects.get(name=BASIC_USER_GRP)
            user.groups.add(group)
        elif user_type == JUDGE:
            group = Group.objects.get(name=JUDGE_GRP)
            user.groups.add(group)
