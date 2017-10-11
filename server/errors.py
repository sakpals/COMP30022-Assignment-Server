error_list = {
    'UnauthorisedError': {
        'message': {'error' : 'Unauthorised'},
        'status': 401,
    },
    'UserAlreadyExistsError': {
        'message': {'error' : "A user with that username already exists."},
        'status': 409,
    },
    'SelfSpecifiedError': {
        'message': {'error' : "Cannot specify yourself as an argument"},
        'status': '400',
    },
    'AlreadySentFriendRequestError': {
        'message': {'error' : "Already requested friend"},
        'status': 400,
    },
    'AlreadyFriendsError': {
        'message': {'error' : "You are already friends with this person"},
        'status': 400,
    },
    'LocationNotStored': {
        'message': {'error' : "Location is not stored for either you or the target"},
        'status': 404,
    },
    'ChannelAlreadyExists': {
        'message': {'error' : "Channel already exists"},
        'status': 409,
    },
    'AlreadyChannelMember': {
        'message': {'error' : "Already a member of this channel"},
        'status': 409,
    },
    'NotChannelMember': {
        'message': {'error' : "Not a member of this channel"},
        'status': 400,
    },
    'InvalidJSON': {
        'message': {'error' : "Supplied parameter is invalid JSON"},
        'status': 400,
    },

    # External errors:
    'NoResultFound': { # sqlalchemy.orm.exc.NoResultFound
        'message': {'error' : "Not Found"},
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

class InvalidJSON(Exception):
    pass
