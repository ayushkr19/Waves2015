from django.contrib.auth.models import Group, User
from rest_framework import permissions
from constants import *

def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    :param user:
    :param group_name:
    :return: Bool
    """
    return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()

class HasAllGroupsPermission(permissions.BasePermission):
    """
    Ensure user is in required groups
    """
    def has_permission(self, request, view):
        # Get a mapping of methods to required groups
        required_groups_mapping = getattr(view, 'required_groups', {})

        # Determine the required groups for this request method
        required_groups = required_groups_mapping.get(request.method, [])

        # Return True if user has all the required groups
        return all([is_in_group(request.user, group_name) for group_name in required_groups])

class HasAtLeastOneGroupPermission(permissions.BasePermission):
    """
    Ensure user is in one of the required groups
    """

    def has_permission(self, request, view):
        # Get a mapping of methods to required groups
        required_groups_mapping = getattr(view, 'required_groups', {})

        # Determine the required groups for this request method
        required_groups = required_groups_mapping.get(request.method, [])

        # Return True if user is anonymous and anonymous users are allowed
        if request.user.is_anonymous() and ANONYMOUS_USER_GRP in required_groups:
            return True

        # Return True if user is in any of the group
        return any([is_in_group(request.user, group_name) for group_name in required_groups])

class IsOwnerOrSuperuser(permissions.BasePermission):
    """
    Ensure whether user is the owner or the user is a superuser
    """

    def has_permission(self, request, view):

        # Get username which has been passed from the URL
        username = view.kwargs['username']

        print('\n Username : ')
        print(username)

        # Retrieve user from the username
        # Using the fact that filter returns QuerySets, and that usernames are unique
        # Done so that this returns None instead of raising DoesNotExist exception
        user = User.objects.filter(username=username).first()

        if user:
            if request.user.is_superuser:
                return True
            else:
                print(user == request.user)
                return user == request.user
        else:
            return False
