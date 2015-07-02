__author__ = 'ayush'

# Constants

# User types
CONTENT_MODIFIERS = 'EventContentEditors'
EVENT_MANAGERS = 'EventManagers'
EVENTS_HEAD = 'EventsHead'
PARTICIPANT = 'Participant'
JUDGE = 'Judges'
BASIC_USER = 'BasicUsers'
COCO = 'CoCo'
DEVELOPER = 'Developers'
# Group names
ANONYMOUS_USER_GRP = 'AnonymousUser'
CONTENT_MODIFIERS_GRP = 'EventContentEditors'
DEVELOPERS_GRP = 'Developers'
COCO_GRP = 'CoCo'
EVENT_MANAGERS_GRP = 'EventManagers'
JUDGE_GRP = 'Judges'
BASIC_USER_GRP = 'BasicUsers'
PARTICIPANT_GRP = 'Participant'

ALL_GRPS_EXCEPT_ANONYMOUS_USER = [CONTENT_MODIFIERS_GRP, DEVELOPERS_GRP, COCO_GRP, EVENT_MANAGERS_GRP,
            JUDGE_GRP, BASIC_USER_GRP, PARTICIPANT_GRP]
ALL_GRPS = [ANONYMOUS_USER_GRP] + ALL_GRPS_EXCEPT_ANONYMOUS_USER

USER_TYPE_CHOICES = (
    (CONTENT_MODIFIERS, 'Content Modifiers'),
    (EVENT_MANAGERS, 'Event Managers'),
    (EVENTS_HEAD, 'Events Head'),
    (PARTICIPANT, 'Participant'),
    (JUDGE, 'Event Judge'),
    (BASIC_USER, 'Basic Default User'),
    (COCO, 'COCO'),
    (DEVELOPER, 'Developers')
)

# Error responses
NO_PROFILE_FOR_USER_ERROR_MESSAGE = {'detail': 'Profile does not exist for the specified User'}
NO_USER_WITH_SPECIFIED_USERNAME_ERROR_MESSAGE = {'detail': 'User does not exist with the specified username'}