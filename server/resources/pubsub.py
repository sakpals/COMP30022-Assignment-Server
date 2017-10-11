from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from common.datatypes import json_string
from pubsub.engine import Router, Channel, Message, messages_marshal
from models.user import User

class ChannelCRUD(Resource):
    @authenticate
    def put(self, channel_name):
        if channel_name.startswith("user_"):
            raise UnauthorisedError()

        parser = reqparse.RequestParser()
        parser.add_argument('persistent', type=bool, required=True, help="Persistent option required")
        args = parser.parse_args()

        Router.new_channel(channel_name, request.user, args['persistent'])
        return {}, 201

    @authenticate
    def delete(self, channel_name):
        if channel_name.startswith("user_"):
            raise UnauthorisedError()

        Router.delete_channel(channel_name, request.user)
        return {}, 200

class ChannelJoin(Resource):
    @authenticate
    def post(self, channel_name):
        if channel_name.startswith("user_"):
            raise UnauthorisedError()

        Router.join_channel(channel_name, request.user)
        return {}, 200

class ChannelPart(Resource):
    @authenticate
    def post(self, channel_name):
        if channel_name.startswith("user_"):
            raise UnauthorisedError()

        Router.part_channel(channel_name, request.user)
        return {}, 200

class ChannelMessage(Resource):
    @authenticate
    def post(self, channel_name):
        parser = reqparse.RequestParser()
        parser.add_argument('type', required=True, help="type is required")
        parser.add_argument('data', type=json_string, required=True, help="data is required")
        args = parser.parse_args()

        if channel_name.startswith("user_"):
            channel = Channel.find(channel_name, False)
            if channel == None:
                username = channel_name[5:]
                user = User.find(username)
                channel = Router.new_channel(channel_name, user, True)
        else:
            channel = Channel.find(channel_name)

        message = Message.new(channel, request.user, args['type'], args['data'])

        Router.send(message)

    @authenticate
    @marshal_with(messages_marshal)
    def get(self, channel_name):
        if channel_name.startswith("user_"):
            if ("user_"+request.user.name) != channel_name:
                raise UnauthorisedError()

        parser = reqparse.RequestParser()
        parser.add_argument('from')
        parser.add_argument('to')
        args = parser.parse_args()

        return {"messages": Router.get_messages(channel_name, args['from'], args['to'])}
