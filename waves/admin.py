from django.contrib import admin

# Register your models here.
from waves.models import *

admin.site.register(Event)

def get_user_type(object):
    """
    Method to return user type
    """
    return object.get_user_type_display()
# Setting these attributes for column name & sorting.
get_user_type.short_description = 'User type'
get_user_type.admin_order_field = 'user_type'

def get_user_groups(object):
    """
    Return the groups that the user belongs to
    """
    return [str(group) for group in object.user.groups.all()]


class ProfileAdmin(admin.ModelAdmin):
    """
    To display profiles in a list. Easy on the eyes.
    """
    list_display = ('user', get_user_type, get_user_groups, 'phone_num', 'created_at', 'modified_at')
    list_filter = ('user_type', 'created_at', 'modified_at')

admin.site.register(Profile, ProfileAdmin)

admin.site.register(Update)
