from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from common.auth import authenticate
from pubsub.engine import Router

class ChannelCRUD(Resource):
    @authenticate
    def put(self, channel_name):
        Router.new_channel(channel_name, request.user)
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
        parser.add_argument('message', required=True, help="message is required")
        args = parser.parse_args()

        message = {
            'user': request.user.username,
            'message': args.message,
        }

        Router.message_channel(channel_name, message)
