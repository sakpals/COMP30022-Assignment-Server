error_list = {
    'UnauthorisedError': {
        'message': 'Unauthorised',
        'status': 401,
    },
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'NotFoundError': {
        'message': "Not Found",
        'status': 404,
    },
    'AlreadySentFriendRequestError': {
        'message': "Already requested friend",
        'status': 400,
    },
}

class UnauthorisedError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class NotFoundError(Exception):
    pass

class AlreadySentFriendRequestError(Exception):
    pass
