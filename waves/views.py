from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from waves.models import *
from waves.permissions import *
from waves.serializers import *
from rest_framework import status
from constants import *
from django.core.exceptions import ObjectDoesNotExist



# Create your views here.

class EventList(generics.ListCreateAPIView):
    """
    List all events. Allow creation if authorized.
    """
    permission_classes = (HasAtLeastOneGroupPermission, )
    required_groups = {
        'GET':  ALL_GRPS,
        'POST': [CONTENT_MODIFIERS_GRP],
        'PUT': [CONTENT_MODIFIERS_GRP]
    }
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    List details of an event. Allow it to be modified if authorized
    """
    permission_classes = (HasAtLeastOneGroupPermission, )
    required_groups = {
        'GET':  ALL_GRPS,
        'POST': [CONTENT_MODIFIERS_GRP],
        'PUT': [CONTENT_MODIFIERS_GRP],
        'DELETE': [CONTENT_MODIFIERS_GRP]
    }
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'subtitle'


class ProfileCreate(APIView):
    """
    Allow creation of profiles. This creates the user as well as the Profile.
    """
    # TODO: Fix potential security risk as users can be created of any type.
    # permission_classes = (permissions.IsAdminUser, )

    def post(self, request, format=None):
        print('\n In view post, going to serialize request.data using AnyUserSerializer')
        print('\n Printing the request.data : ')
        print(request.data)

        profile = AnyUserSerializer(data=request.data)

        print('\nIn view : Printing profile:')
        print(profile)

        if profile.is_valid(raise_exception=True):
            print('\n In view : Printing profile data:')
            print(profile.data)

            print('\n In view : Profile data valid. Saving.')
            profile.save()
            return Response(status=status.HTTP_201_CREATED)



class ProfileListView(generics.ListAPIView):
    """
    Allow admin users to view list of all profiles
    """
    permission_classes = (permissions.IsAdminUser, )
    queryset = Profile.objects.all()
    serializer_class = AnyUserSerializer

class ProfileDetailView(APIView):
    """
    For specific users to view their profile information, or for superusers to view information
    about every user
    """
    permission_classes = (IsOwnerOrSuperuser, )

    def get(self, request, username, format=None):

        username = self.kwargs['username']
        print(username)

        user = User.objects.filter(username=username).first()
        if user:

            try:
                profile = user.profile
            except ObjectDoesNotExist:
                return Response(data=NO_PROFILE_FOR_USER_ERROR_MESSAGE,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            profile_serializer = AnyUserSerializer(profile)
            return Response(profile_serializer.data)
        else:
            return Response(data=NO_USER_WITH_SPECIFIED_USERNAME_ERROR_MESSAGE,
                            status=status.HTTP_404_NOT_FOUND)

    def put(self, request, username, format=None):
        """
        To update a profile of a user, use put. In the user json, do not include username
        """
        username = self.kwargs['username']
        print('Username to be updated ' + username)
        user = User.objects.filter(username=username).first()
        if user:
            try:
                profile = user.profile
            except ObjectDoesNotExist:
                return Response(data=NO_PROFILE_FOR_USER_ERROR_MESSAGE,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            profile_serializer = ProfileSerializer(profile, data=request.data, partial=True)
            print('\nIn view : Printing profile:')
            print(profile)

            if profile_serializer.is_valid(raise_exception=True):
                print('\n In view : Printing profile data:')
                print(profile_serializer.data)

                print('\n In view : Profile data valid. Saving.')
                profile_serializer.save()
                return Response(status=status.HTTP_200_OK)

        else:
            return Response(data=NO_USER_WITH_SPECIFIED_USERNAME_ERROR_MESSAGE,
                            status=status.HTTP_404_NOT_FOUND)

# class EventManagersListView(generics.ListAPIView):
#     """
#     Return a list of event content editors
#     (people who can be added as event managers)
#     """
#     permission_classes = (HasAtLeastOneGroupPermission, )
#     required_groups = {
#         'GET':  [CONTENT_MODIFIERS_GRP],
#     }
#     serializer_class = ProfileSerializer
#
#     def get_queryset(self):
#         return Profile.objects.filter(user__groups__name__in=[EVENT_MANAGERS_GRP])


class EventManagerOfEvents(APIView):
    """
    Handle event managers of an event
    """
    permission_classes = (HasAtLeastOneGroupPermission, )
    required_groups = {
        'GET': [CONTENT_MODIFIERS_GRP],
        'POST': [CONTENT_MODIFIERS_GRP],
        'DELETE': [CONTENT_MODIFIERS_GRP]
    }

    def get(self, request, format=None):
        """
        Return a list of event managers
        """
        profiles = Profile.objects.filter(user_type=EVENT_MANAGERS)
        profiles_serializer = ProfileSerializer(profiles, many=True)
        return Response(status=status.HTTP_200_OK, data=profiles_serializer.data)

    def post(self, request, format=None):
        """
        Add event managers to an event
        """
        print('Request data: ')
        print(request.data)
        event_name = request.data['event_name']
        event_managers = request.data['event_managers']

        event = Event.objects.filter(name=event_name).first()
        if event:
            for event_manager in event_managers:
                profile = Profile.objects.get(user__username=event_manager['name'])
                if not Group.objects.get(name=EVENT_MANAGERS_GRP) in profile.user.groups.all():
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=HACKER_MESSAGE)
                event.event_managers.add(profile)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_EVENT_WITH_SPECIFIED_NAME)

    def delete(self, request, format=None):
        """
        Remove event managers from an event
        """
        print('Delete request data:')
        print(request.data)

        event_name = request.data['event_name']
        event_managers = request.data['event_managers']

        event = Event.objects.filter(name=event_name).first()
        if event:
            for event_manager in event_managers:
                profile = Profile.objects.get(user__username=event_manager['name'])
                if not Group.objects.get(name=EVENT_MANAGERS_GRP) in profile.user.groups.all():
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=HACKER_MESSAGE)
                event.event_managers.remove(profile)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_EVENT_WITH_SPECIFIED_NAME)