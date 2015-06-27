from django.contrib.auth.models import User, Group
from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from waves.models import Profile
from waves.views import ProfileCreate
from constants import *


class ProfileTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # Create all groups necessary
        for group_name in ALL_GRPS:
            Group.objects.create(name=group_name)

        # Create a user (just for fun)
        user = User.objects.create_user(username='test_username', email='test@gmail.com',
                                        password='test_password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()
        # Create profile for the user
        profile = Profile.objects.create(user=user, user_type=BASIC_USER, phone_num='95553')
        profile.save()

        # Create a user without profile
        user = User.objects.create_user(username='test_username_no_profile', email='test2@gmail.com',
                                        password='test_password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()

    def test_user_created(self):
        """
        Test if a user is created successfully or not
        """
        view = ProfileCreate.as_view()
        request = self.factory.post('/profile/',
                                    data={
                                        'user': {
                                            'username': 'username',
                                            'email': 'usr@gmail.com',
                                            'password': 'passwd',
                                            'first_name': 'first',
                                            'last_name': 'last'
                                        },
                                        'user_type': BASIC_USER,
                                        'phone_num': '9637383571'

                                    }, format='json')
        response = view(request)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='username')
        self.assertEquals(user.first_name, 'first')
        self.assertEquals(user.last_name, 'last')
        self.assertEquals(user.email, 'usr@gmail.com')

        self.assertEquals(user.profile.user_type, 'BasicUsers')
        self.assertEquals(user.profile.phone_num, '9637383571')

    def test_user_create_bad_request(self):
        """
        Test user not created because of bad request
        """
        view = ProfileCreate.as_view()
        request = self.factory.post('/profile/',
                                    data={
                                        'user': {
                                            'email': 'usr@gmail.com',
                                            'password': 'passwd',
                                            'first_name': 'first',
                                            'last_name': 'last'
                                        },
                                        'user_type': BASIC_USER,
                                        'phone_num': '9637383571'

                                    }, format='json')
        response = view(request)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEquals(response.data, )

        request = self.factory.post('/profile/',
                                    data={
                                        'user': {
                                            'username': 'username',
                                            'email': 'usr@gmail.com',
                                            'first_name': 'first',
                                            'last_name': 'last'
                                        },
                                        'user_type': BASIC_USER,
                                        'phone_num': '9637383571'

                                    }, format='json')
        response = view(request)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_being_added_to_group(self):
        """
        Test users are added to group depending on their user type
        """

        for group_name in ALL_GRPS_EXCEPT_ANONYMOUS_USER:

            user = User.objects.create_user(username='username', email='uer@gmail.com',
                                            password='password')
            user.save()
            profile = Profile.objects.create(user=user, user_type=group_name, phone_num='95553')
            profile.save()

            group = Group.objects.get(name=group_name)
            self.assertEquals(group.user_set.filter(username=user.username).first(), user)

            user.delete()
            profile.delete()

    def test_user_can_access_his_profile(self):
        """
        Test users are able to view information of their own profile, and they cannot access
        another user's profile unless they are a superuser
        """
        user = User.objects.create_user(username='ayushkrcm', email='uer@gmail.com',
                                        password='ayushd')
        user.save()
        profile = Profile.objects.create(user=user, user_type=BASIC_USER, phone_num='95553')
        profile.save()

        client = APIClient()

        # Get own profile without providing authentication information
        response = client.get('/profile/ayushkrcm/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Get own profile with Basic authentication
        encoded = 'YXl1c2hrcmNtOmF5dXNoZA=='
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)
        response = client.get('/profile/ayushkrcm/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get another user's information
        response = client.get('/profile/test_username/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Setting user to superuser
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Get own profile with Basic authentication
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)
        response = client.get('/profile/ayushkrcm/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get another user's information
        response = client.get('/profile/test_username/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get a user without a profile's info
        response = client.get('/profile/test_username_no_profile/')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEquals(response.data, NO_PROFILE_FOR_USER_ERROR_MESSAGE)

        # Get a non existent user's profile
        response = client.get('/profile/test_username_nonexistent/')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data, NO_USER_WITH_SPECIFIED_USERNAME_ERROR_MESSAGE)
