from flask_restful import reqparse
from datetime import datetime
from functools import wraps
from flask import request

from models.user import Token 
from db import db

# Attempts to load user from token sent in request
# Returns None on error
# Returns (User, Token) on success
def find_account():
    parser = reqparse.RequestParser()
    parser.add_argument('access_token')
    args = parser.parse_args()

    if args['access_token'] == None:
        return None

    token = Token.query.filter_by(token_string = args['access_token']).first()
    if token == None:
        return None

    token.last_use = datetime.utcnow()

    db.session.add(token)
    db.session.commit()

    return (token.user, token)
    
# Decorator function used to authenticate requests
# Sets request.user, request.access_token on success
# Returns 401 on failure
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        acct = find_account()
        if acct:
            request.user = acct[0]
            request.access_token = acct[1]
            return func(*args, **kwargs)

        return {}, 401 
    return wrapper
