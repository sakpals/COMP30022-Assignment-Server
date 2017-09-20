from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from common.datatypes import json_string
from pubsub.engine import Router, Channel, Message, message_marshal

class ChannelCRUD(Resource):
    @authenticate
    def put(self, channel_name):
        parser = reqparse.RequestParser()
        parser.add_argument('persistent', type=bool, required=True, help="Persistent option required")
        args = parser.parse_args()

        Router.new_channel(channel_name, request.user, args['persistent'])
        return {}, 201

    @authenticate
    def delete(self, channel_name):
        Router.delete_channel(channel_name, request.user)
        return {}, 200

class ChannelJoin(Resource):
    @authenticate
    def post(self, channel_name):
        Router.join_channel(channel_name, request.user)
        return {}, 200

class ChannelPart(Resource):
    @authenticate
    def post(self, channel_name):
        Router.part_channel(channel_name, request.user)
        return {}, 200

class ChannelMessage(Resource):
    @authenticate
    def post(self, channel_name):
        parser = reqparse.RequestParser()
        parser.add_argument('type', required=True, help="type is required")
        parser.add_argument('data', type=json_string, required=True, help="data is required")
        args = parser.parse_args()

        channel = Channel.find(channel_name)

        message = Message.new(channel, request.user, args['type'], args['data'])

        Router.send(message)

    @authenticate
    @marshal_with(message_marshal)
    def get(self, channel_name):
        parser = reqparse.RequestParser()
        parser.add_argument('from')
        parser.add_argument('to')
        args = parser.parse_args()

        return Router.get_messages(channel_name, args['from'], args['to'])
