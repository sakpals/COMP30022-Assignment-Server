# Add Accept Remove IncomingRequest OutgoingRequest
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from models.user import User, profile_fields
from models.friends import FriendshipRequest, Friendship
from errors import *
from db import db

class FriendAdd(Resource):
    # Called on creating friend request. Username is target friend
    @authenticate
    def post(self, username):
        target = User.find(username)

        if target == request.user:
            raise SelfSpecifiedError()

        friendship = Friendship.query.filter_by(me=request.user, friend=target).first()
        if friendship != None:
            raise AlreadyFriendsError()

        friend_request = FriendshipRequest.query.filter_by(user_from=request.user, user_to=target).first()
        if friend_request != None:
            raise AlreadySentFriendRequestError()

        friend_request = FriendshipRequest(request.user, target)
        db.session.add(friend_request)
        db.session.commit()

        return {}, 201

class FriendList(Resource):

    friends_fields = {
        'friends': fields.List(fields.Nested({
            'profile': fields.Nested(profile_fields, attribute="friend")
        }))
    }

    @marshal_with(friends_fields)
    @authenticate
    def get(self):
        return {"friends": request.user.friends}

class FriendAccept(Resource):
    @authenticate
    def post(self, request_token):
        friend_request = FriendshipRequest.query.filter_by(user_to=request.user, token=request_token).one()

        friendship = Friendship.query.filter_by(me=request.user, friend=friend_request.user_from).first()
        if friendship != None:
            db.session.delete(friend_request)
            db.session.commit()
            raise AlreadyFriendsError()

        db.session.delete(friend_request)
        Friendship.add_pair(friend_request.user_from, friend_request.user_to)
        db.session.commit()

        return {}, 200

class FriendRemove(Resource):

    @authenticate
    def post(self, username):

        friend = User.find(username)
        friendship = Friendship.query.filter_by(me=request.user, friend=friend).one()

        if friendship.friend == request.user:
            raise SelfSpecifiedError()

        Friendship.remove_friendship(friendship)
        db.session.commit()

        return {}

class FriendIncomingRequests(Resource):

    incoming_fields = {
        'requests': fields.List(fields.Nested({
            'token': fields.String,
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
            'profile': fields.Nested(profile_fields, attribute='user_to')
        }))
    }

    @marshal_with(outgoing_fields)
    @authenticate
    def get(self):
        return {"requests": request.user.outgoing_friend_requests}
