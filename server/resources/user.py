from flask_restful import Resource, reqparse
from flask import request

from common.auth import authenticate
from models.user import User
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
            return None, 401
        
        #Attempt login
        token = u.login(args["password"])

        if token == None:
            return None, 401
        else:
            return {'access_token': token}

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
            return {"message": "Username already taken"}, 409

        # We're all good, user created
        return {}, 201

class UserProfile(Resource):
    def get(self, user_id):
        pass

    def put(self, user_id):
        pass
