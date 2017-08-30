from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from models.user import User
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
        u = User.query.filter_by(username=args["username"]).first()
        if u == None:
            raise UnauthorisedError()
        
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
        except Exception as e:
            # Should be more critical in Exception handling, rather than just 
            # catching all errors. Particularly this catches the case where
            # a tables unique constraint fails
            raise UserAlreadyExistsError()

        # We're all good, user created
        return {}, 201

class UserProfile(Resource):
    def authorised_to_get(self, viewer, target):
        return True

    # Defines the fields we want to return on get. Obviously we don't want
    # to return users passwords on any request
    profile_fields = {
        'username': fields.String,
        'description': fields.String,
        'avatar_url': fields.String,
    }

    @marshal_with(profile_fields)
    @authenticate
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user == None:
            raise NotFoundError()

        if not self.authorised_to_get(request.user, user):
            raise UnauthorisedError()

        return user

    @authenticate
    def put(self, username):
        if username != request.user.username:
            raise UnauthorisedError()
        pass
