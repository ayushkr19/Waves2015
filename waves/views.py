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
                return Response(data={'detail': 'Profile does not exist for the specified User'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            profile_serializer = AnyUserSerializer(profile)
            return Response(profile_serializer.data)
        else:
            return Response(data={'detail': 'User does not exist with the specified username'},
                            status=status.HTTP_400_BAD_REQUEST)
