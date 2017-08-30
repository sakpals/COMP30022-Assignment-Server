from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from common.datatypes import avatar_url
from models.user import User, profile_fields
from errors import *
from db import db

class UserLogin(Resource):
    def post(self):
        # Get args
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='username required')
        parser.add_argument('password', required=True, help='password required')
        args = parser.parse_args()
        
        # Find user, TODO: fix timing attack
        u = User.find(args["username"])
        
        #Attempt login
        access_token = u.login(args["password"])

        if access_token == None:
            raise UnauthorisedError()
        else:
            return {'access_token': access_token}

class UserLogout(Resource):
    @authenticate 
    def post(self):
        # Delete current access token
        db.session.delete(request.access_token)
        db.session.commit()
        return {}, 200

class UserRegister(Resource):
    def post(self):
        # Get args
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='username required')
        parser.add_argument('password', required=True, help='password required')
        parser.add_argument('description')
        parser.add_argument('avatar_url')
        args = parser.parse_args()
        
        # Create user and attempt saving
        user = User.from_args(args)
        try:
            db.session.add(user)
            db.session.commit()
            access_token = user.add_token().token_string
        except Exception as e:
            # Should be more critical in Exception handling, rather than just 
            # catching all errors. Particularly this catches the case where
            # a tables unique constraint fails
            raise UserAlreadyExistsError()

        # We're all good, user created
        return {'access_token': access_token}, 201

class UserProfile(Resource):

    @marshal_with(profile_fields)
    @authenticate
    def get(self, username):
        user = User.find(username)

        if not self.authorised_to_get(request.user, user):
            raise UnauthorisedError()

        return user

    @marshal_with(profile_fields)
    @authenticate
    def put(self, username):
        user = User.find(username)

        if not self.authorised_to_set(request.user, user):
            raise UnauthorisedError()

        parser = reqparse.RequestParser()
        parser.add_argument('description')
        parser.add_argument('avatar_url', type=avatar_url, help='Invalid URL: {error_msg}' )
        args = parser.parse_args()

        for arg in args:
            setattr(user, arg, args[arg])

        db.session.add(user)
        db.session.commit()

        return user

    # The following two methods are authorisation for get/set of profile data.
    # This should probably be moved into a separate module soon, but for now
    # is handy to have local, obviously people can only set their own profile,
    # but everyone can read everyone elses (for now)
    def authorised_to_get(self, viewer, target):
        return True

    def authorised_to_set(self, setter, target):
        return setter.username == target.username
