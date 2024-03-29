import base64
from django.contrib.auth.models import User, Group
from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from waves.models import *
from waves.views import ProfileCreate, EventList
from constants import *


class ProfileTests(APITestCase):
    """
    Tests related to profiles
    """

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
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data, NO_USER_WITH_SPECIFIED_USERNAME_ERROR_MESSAGE)

    def user_can_edit_his_profile(self):
        """
        Test whether users can edit their profile information
        # TODO: (Group checking not done yet)
        """
        user = User.objects.create_user(username='ayushkrcm', email='uer@gmail.com',
                                        password='ayushd')
        user.save()
        profile = Profile.objects.create(user=user, user_type=BASIC_USER, phone_num='95553')
        profile.save()

        client = APIClient()

        new_profile_data = {
            'phone_num': '9637282571',
            'user': {
                'first_name': 'Ayush',
                'last_name': 'Kumar',
                'email': 'ayush@gmail.com',
                'password': 'ayushkumar'
            }

        }
        # Edit own profile without providing authentication information
        response = client.put('/profile/ayushkrcm/', data=new_profile_data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Edit own profile with Basic authentication
        encoded = base64.b64encode('ayushkrcm:ayushd')
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)
        response = client.put('/profile/ayushkrcm/', data=new_profile_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get user object and check updated fields
        user = User.objects.get(username='ayushkrcm')
        self.assertEquals(user.first_name, 'Ayush')
        self.assertEquals(user.last_name, 'Kumar')
        self.assertEquals(user.email, 'ayush@gmail.com')
        self.assertEquals(user.profile.phone_num, '9637282571')

        # Get profile data using old password
        response = client.get('/profile/ayushkrcm/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Set credentials to new password
        encoded = base64.b64encode('ayushkrcm:ayushkumar')
        client.credentials()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Get profile data using new password
        response = client.get('/profile/ayushkrcm/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Edit another user's information
        response = client.put('/profile/test_username/', data=new_profile_data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

class EventTests(APITestCase):
    """
    Tests related to events
    """
    event1_data = {
        'name': 'Event 1',
        'description': 'Description',
        'subtitle': 'Subtitle',
        'event_url': 'http://www.google.com'
    }

    event2_data = {
        'name': 'Event 2',
        'description': 'Description 2',
        'subtitle': 'Bla Bla',
        'event_url': 'http://www.fb.com'
    }

    em_to_event_data = {
        "event_name": "Event 1",
        "event_managers": [
            {
                "name": "test_username_em1"
            },
            {
                "name": "test_username_em2"
            }
        ]

    }

    all_event_data = [event1_data, event2_data]

    def setUp(self):
        self.factory = APIRequestFactory()

        # Create all groups necessary
        for group_name in ALL_GRPS:
            Group.objects.create(name=group_name)

        # Create a user (just for fun)
        user = User.objects.create_user(username='test_username_cm', email='test@gmail.com',
                                        password='password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()
        # Create profile for the user
        profile = Profile.objects.create(user=user, user_type=CONTENT_MODIFIERS, phone_num='95553')
        profile.save()

        # Create a superuser
        superuser = User.objects.create_user(username='ayushkrcm', email='su@gmail.com',
                                             password='ayushd')
        superuser.first_name = 'first_su'
        superuser.last_name = 'last_su'
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()
        # Create profile for the superuser
        profile = Profile.objects.create(user=superuser, user_type=CONTENT_MODIFIERS, phone_num='95553')
        profile.save()

        # Create events

        event1 = Event.objects.create(**self.event1_data)
        event1.save()

        event2 = Event.objects.create(**self.event2_data)
        event2.save()

        # Create event managers
        user = User.objects.create_user(username='test_username_em1', email='test@gmail.com',
                                        password='password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()
        # Create profile for the user
        profile = Profile.objects.create(user=user, user_type=EVENT_MANAGERS, phone_num='95553')
        profile.save()

        user = User.objects.create_user(username='test_username_em2', email='test@gmail.com',
                                        password='password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()
        # Create profile for the user
        profile = Profile.objects.create(user=user, user_type=EVENT_MANAGERS, phone_num='95553')
        profile.save()

    def test_event_created(self):
        """
        Test that the event has been created in the setUp method
        """
        event1 = Event.objects.get(name='Event 1')
        self.assertEquals(event1.description, 'Description')
        self.assertEquals(event1.subtitle, 'Subtitle')
        self.assertEquals(event1.event_url, 'http://www.google.com')

    def test_event_create(self):
        """
        Test event creation through the API.
        Only users belonging to the CM group (or superuser) can create events
        """
        client = APIClient()
        event_data = {
            'name': 'Event 3',
            'description': 'Description',
            'subtitle': 'subtitle',
            'event_url': 'http://www.gogle.com'
        }

        # Post data from an unauthenticated user
        response = client.post('/events/', data=event_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Set authentication details for other group
        encoded = base64.b64encode('test_username:test_password')
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Post data from authenticated user belonging to the other group
        response = client.post('/events/', data=event_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Set authentication details for necessary group
        encoded = base64.b64encode('test_username_cm:password')
        client.credentials()  # To clear auth credentials
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Post data from authenticated user belonging to the necessary group
        response = client.post('/events/', data=event_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        Event.objects.get(name='Event 3').delete()

        # Setting authentication details for superuser
        encoded = base64.b64encode('ayushkrcm:ayushd')
        client.credentials()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Posting data from superuser
        response = client.post('/events/', data=event_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_list_events(self):
        """
        Test whether the list of events are being retrieved
        """
        client = APIClient()

        response = client.get('/events/', format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        for i in range(self.all_event_data.__len__()):
            self.assertEquals(self.all_event_data[i]['name'], response.data[i]['name'])
            self.assertEquals(self.all_event_data[i]['description'], response.data[i]['description'])
            self.assertEquals(self.all_event_data[i]['subtitle'], response.data[i]['subtitle'])
            self.assertEquals(self.all_event_data[i]['event_url'], response.data[i]['event_url'])

    def test_individual_event(self):
        """
        Test whether single event's details are being retrieved or not
        """
        client = APIClient()

        response = client.get('/events/1/', format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertEquals(self.all_event_data[0]['name'], response.data['name'])
        self.assertEquals(self.all_event_data[0]['description'], response.data['description'])
        self.assertEquals(self.all_event_data[0]['subtitle'], response.data['subtitle'])
        self.assertEquals(self.all_event_data[0]['event_url'], response.data['event_url'])
        self.assertNotEquals(None, response.data['created_at'])
        self.assertNotEquals(None, response.data['modified_at'])

        response = client.get('/events/2/', format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertEquals(self.all_event_data[1]['name'], response.data['name'])
        self.assertEquals(self.all_event_data[1]['description'], response.data['description'])
        self.assertEquals(self.all_event_data[1]['subtitle'], response.data['subtitle'])
        self.assertEquals(self.all_event_data[1]['event_url'], response.data['event_url'])
        self.assertNotEquals(None, response.data['created_at'])
        self.assertNotEquals(None, response.data['modified_at'])

    def test_get_event_managers(self):
        """
        Test whether event managers are being fetched properly
        """
        client = APIClient()

        response = client.get('/eventmanagers/', format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Setting authentication details for content modifier
        encoded = base64.b64encode('test_username_cm:password')
        client.credentials()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        response = client.get('/eventmanagers/', format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        for profile in response.data:
            self.assertEquals(profile['user']['first_name'], 'first')
            self.assertEquals(profile['user']['last_name'], 'last')
            self.assertEquals(profile['user']['email'], 'test@gmail.com')
            self.assertEquals(profile['user_type'], EVENT_MANAGERS)
            self.assertEquals(profile['phone_num'], '95553')
            self.assertNotEquals(None, profile['user']['username'])

    def test_post_add_event_manager_to_event(self):
        """
        Test whether event managers are added to the event or not
        """
        client = APIClient()

        response = client.post('/eventmanagers/', format='json', data=self.em_to_event_data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Setting authentication details for content modifier
        encoded = base64.b64encode('test_username_cm:password')
        client.credentials()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        response = client.post('/eventmanagers/', format='json', data=self.em_to_event_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        event = Event.objects.get(name='Event 1')
        em1 = event.event_managers.all()[0]
        em2 = event.event_managers.all()[1]
        self.assertEquals(em1.user.username, 'test_username_em1')
        self.assertEquals(em2.user.username, 'test_username_em2')

    def test_delete_event_manager_from_event(self):
        """
        Test whether event managers are being removed from the event or not
        """
        client = APIClient()

        response = client.delete('/eventmanagers/', format='json', data=self.em_to_event_data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Setting authentication details for content modifier
        encoded = base64.b64encode('test_username_cm:password')
        client.credentials()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        response = client.delete('/eventmanagers/', format='json', data=self.em_to_event_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        event = Event.objects.get(name='Event 1')
        self.assertFalse(event.event_managers.all())

class UpdateTest(APITestCase):
    """
    Tests related to updates
    """
    event1_data = {
        'name': 'Event 1',
        'description': 'Description',
        'subtitle': 'Subtitle',
        'event_url': 'http://www.google.com'
    }

    event2_data = {
        'name': 'Event 2',
        'description': 'Description 2',
        'subtitle': 'Bla Bla',
        'event_url': 'http://www.fb.com'
    }

    update_data1 = {
        'heading': 'Head 1',
        'description': 'Desc',
        'general_update': True
    }

    update_data2 = {
        'heading': 'Head 2',
        'description': 'Desc',
        'general_update': False
    }

    all_update_data = [update_data1, update_data2]

    def setUp(self):
        # Create all groups necessary
        for group_name in ALL_GRPS:
            Group.objects.create(name=group_name)

        # Create a user (just for fun)
        user = User.objects.create_user(username='test_username_cm', email='test@gmail.com',
                                        password='password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()
        # Create profile for the user
        profile = Profile.objects.create(user=user, user_type=CONTENT_MODIFIERS, phone_num='95553')
        profile.save()

        # Create a user (just for fun)
        user = User.objects.create_user(username='test_username', email='test@gmail.com',
                                        password='password')
        user.first_name = 'first'
        user.last_name = 'last'
        user.save()
        # Create profile for the user
        profile = Profile.objects.create(user=user, user_type=BASIC_USER_GRP, phone_num='95553')
        profile.save()

        # Create a superuser
        superuser = User.objects.create_user(username='ayushkrcm', email='su@gmail.com',
                                             password='ayushd')
        superuser.first_name = 'first_su'
        superuser.last_name = 'last_su'
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()
        # Create profile for the superuser
        profile = Profile.objects.create(user=superuser, user_type=CONTENT_MODIFIERS, phone_num='95553')
        profile.save()

        # Create events

        event1 = Event.objects.create(**self.event1_data)
        event1.save()

        event2 = Event.objects.create(**self.event2_data)
        event2.save()

        update1 = Update.objects.create(**self.update_data1)
        update1.save()

        update2 = Update.objects.create(**self.update_data2)
        update2.save()

    def test_update_created(self):

        client = APIClient()
        update_data = {
            'heading': 'Update1',
            'description': 'Desc',
            'general_update': 'True'
        }

        # Post data from an unauthenticated user
        response = client.post('/updates/', data=update_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Set authentication details for other group
        encoded = base64.b64encode('test_username:test_password')
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Post data from authenticated user belonging to the other group
        response = client.post('/updates/', data=update_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Set authentication details for necessary group
        encoded = base64.b64encode('test_username_cm:password')
        client.credentials()  # To clear auth credentials
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Post data from authenticated user belonging to the necessary group
        response = client.post('/updates/', data=update_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        update = Update.objects.get(heading='Update1', description='Desc')
        self.assertIsNone(update.for_event)
        self.assertEquals(update.general_update, True)
        self.assertEquals(update.created_by.user, User.objects.get(username='test_username_cm'))

        update_data = {
            'heading': 'Update2',
            'description': 'Desc',
            'general_update': 'False',
            'for_event__subtitle': 'Subtitle'
        }

        response = client.post('/updates/', data=update_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        update = Update.objects.get(heading='Update2', description='Desc')
        self.assertEquals(update.general_update, False)
        self.assertEquals(update.for_event, Event.objects.get(subtitle='Subtitle'))

        # Setting authentication details for superuser
        encoded = base64.b64encode('ayushkrcm:ayushd')
        client.credentials()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded)

        # Posting data from superuser
        response = client.post('/updates/', data=update_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_get_updates(self):

        client = APIClient()
        response = client.get('/updates/', format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        for i in range(self.all_update_data.__len__()):
            self.assertEquals(self.all_update_data[i]['heading'], response.data[i]['heading'])
            self.assertEquals(self.all_update_data[i]['description'], response.data[i]['description'])
            self.assertEquals(self.all_update_data[i]['general_update'], response.data[i]['general_update'])