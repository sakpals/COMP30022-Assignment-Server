error_list = {
    'UnauthorisedError': {
        'message': 'Unauthorised',
        'status': 401,
    },
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'SelfSpecifiedError': {
        'message': "Cannot specify yourself as an argument",
        'status': '400',
    },
    'AlreadySentFriendRequestError': {
        'message': "Already requested friend",
        'status': 400,
    },
    'AlreadyFriendsError': {
        'message': "You are already friends with this person",
        'status': 400,
    },
    'LocationNotStored': {
        'message': "Location is not stored for either you or the target",
        'status': 404,
    },
    'ChannelAlreadyExists': {
        'message': "Channel already exists",
        'status': 409,
    },
    'AlreadyChannelMember': {
        'message': "Already a member of this channel",
        'status': 409,
    },
    'NotChannelMember': {
        'message': "Not a member of this channel",
        'status': 400,
    },

    # External errors:
    'NoResultFound': { # sqlalchemy.orm.exc.NoResultFound
        'message': "Not Found",
        'status': 404,
    },
}

class UnauthorisedError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class SelfSpecifiedError(Exception):
    pass

class AlreadyFriendsError(Exception):
    pass

class AlreadySentFriendRequestError(Exception):
    pass

class LocationNotStored(Exception):
    pass

class ChannelAlreadyExists(Exception):
    pass

class AlreadyChannelMember(Exception):
    pass

class NotChannelMember(Exception):
    pass
