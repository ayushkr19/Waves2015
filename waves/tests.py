from django.contrib.auth.models import User, Group
from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from waves.views import ProfileCreate
from constants import *


class ProfileTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # Create a user (just for fun)
        user = User.objects.create_user(username='test_username', email='test@gmail.com',
                                        password='test_password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()

        # Create all groups necessary
        for group_name in ALL_GRPS:
            Group.objects.create(name=group_name)

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
                                        'user_type': 'BA',
                                        'phone_num': '9637383571'

                                    }, format='json')
        response = view(request)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='username')
        self.assertEquals(user.first_name, 'first')
        self.assertEquals(user.last_name, 'last')
        self.assertEquals(user.email, 'usr@gmail.com')

        self.assertEquals(user.profile.user_type, 'BA')
        self.assertEquals(user.profile.phone_num, '9637383571')

    def test_user_create_bad_request(self):
        """
        Test user not created because of bad request
        :return:
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
                                        'user_type': 'BA',
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
                                        'user_type': 'BA',
                                        'phone_num': '9637383571'

                                    }, format='json')
        response= view(request)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
