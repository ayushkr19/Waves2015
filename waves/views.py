from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from waves.models import Event, Profile
from waves.permissions import HasAllGroupsPermission, HasAtLeastOneGroupPermission
from waves.serializers import EventSerializer,  UserSerializer, AnyUserSerializer
from rest_framework import status
from constants import *


# Create your views here.

class EventList(generics.ListCreateAPIView):
    permission_classes = (HasAtLeastOneGroupPermission, )
    required_groups = {
        'GET':  ALL_GRPS,
        'POST': [CONTENT_MODIFIERS_GRP]
    }
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class ProfileCreate(APIView):

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
    permission_classes = (permissions.IsAdminUser, )
    queryset = Profile.objects.all()
    serializer_class = AnyUserSerializer
