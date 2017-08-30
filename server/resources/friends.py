# Add Accept Remove IncomingRequest OutgoingRequest
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from models.user import User, profile_fields
from models.friends import FriendshipRequest
from errors import *
from db import db

class FriendAdd(Resource):
    # Called on creating friend request. Username is target friend
    @authenticate
    def post(self, username):
        target = User.find(username)
        friend_request = FriendshipRequest.query.filter_by(user_from=request.user, user_to=target).first()
        if friend_request != None:
            raise AlreadySentFriendRequestError()

        friend_request = FriendshipRequest(request.user, target)
        db.session.add(friend_request)
        db.session.commit()

        return {}, 201

class FriendAccept(Resource):
    pass

class FriendRemove(Resource):
    pass

class FriendIncomingRequests(Resource):
    incoming_fields = {
        'requests': fields.List(fields.Nested({
            'profile': fields.Nested(profile_fields, attribute='user_from')
        }))
    }

    @marshal_with(incoming_fields)
    @authenticate
    def get(self):
        return {"requests": request.user.incoming_friend_requests}

class FriendOutgoingRequests(Resource):

    outgoing_fields = {
        'requests': fields.List(fields.Nested({
            'token': fields.String,
            'profile': fields.Nested(profile_fields, attribute='user_to')
        }))
    }

    @marshal_with(outgoing_fields)
    @authenticate
    def get(self):
        return {"requests": request.user.outgoing_friend_requests}
