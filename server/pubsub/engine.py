import json
import gevent
from flask import request
from flask_restful import fields, marshal
from datetime import datetime
from uuid import uuid4

from common.auth import authenticate
from errors import *
from db import db

channel_members = db.Table('pubsub_channel_members',
    db.Column('channel_id', db.Integer, db.ForeignKey('pubsub_channel.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class MessageFormat(fields.Raw):
    def format(self, value):
        return json.loads(value)

message_marshal = {
    'channel': fields.String(attribute="channel.name"),
    'user': fields.String(attribute="user.username"),
    'type': fields.String(attribute="type"),
    'data': MessageFormat(attribute="data"),
    'id' : fields.String(attribute="uuid"),
    'prev': fields.String(attribute="prev_uuid"),
    'next': fields.String(attribute="next_uuid"),
    'server_time': fields.String(attribute="server_time")
}
messages_marshal = {
    'messages': fields.List(fields.Nested(message_marshal))
}

class Message(db.Model):
    __tablename__ = 'pubsub_message'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), index=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('pubsub_channel.id'), index=True)
    channel = db.relationship('Channel', backref=db.backref('messages', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User', backref=db.backref('messages', lazy='dynamic'))
    type = db.Column(db.String(64))
    data = db.Column(db.String(4096))
    next_uuid = db.Column(db.String(16), db.ForeignKey('pubsub_message.id'), nullable=True)
    prev_uuid = db.Column(db.String(16), db.ForeignKey('pubsub_message.id'), nullable=True)
    server_time = db.Column(db.DateTime)

    @staticmethod
    def new(channel, user, msg_type, msg_data):

        msg = Message()
        msg.channel_id = channel.id
        msg.user_id = user.id
        msg.type = msg_type
        msg.data = msg_data

        msg.channel = channel
        msg.user = user

        msg.server_time = datetime.utcnow()

        if channel.persistent:
            # Might be a better way to do this
            msg.next_uuid = str(uuid4())
            db.session.add(msg)
            db.session.commit()

            prev = Message.query.filter(Message.id < msg.id, Message.channel == channel).order_by(Message.id.desc()).first()
            if prev == None:
                msg.uuid = str(uuid4())
            else:
                msg.uuid = prev.next_uuid
                msg.prev_uuid = prev.uuid

            db.session.add(msg)
            db.session.commit()

        return msg

class Channel(db.Model):
    __tablename__ = 'pubsub_channel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
    persistent = db.Column(db.Boolean, default=False)
    users = db.relationship('User', secondary=channel_members,
        backref=db.backref('channels', lazy='dynamic'))

    @staticmethod
    def find(channel_name, fail_not_found=True):
        if fail_not_found:
            return Channel.query.filter_by(name=channel_name).one()
        else:
            return Channel.query.filter_by(name=channel_name).first()

class Router():
    user_to_socket = {}
    channels = {}

    def __init__(self):
        for channel in Channel.query.all():
            channels[channel.name] = channel

    @staticmethod
    def new_channel(channel_name, user, persistent=False):
        channel = Channel()
        channel.name = channel_name
        channel.users.append(user)
        channel.persistent = persistent
        db.session.add(channel)
        try:
            db.session.commit()
        except Exception as e:
            raise ChannelAlreadyExists()

        return channel

    @staticmethod
    def join_channel(channel_name, user):
        channel = Channel.find(channel_name)
        if user in channel.users:
            raise AlreadyChannelMember()
        else:
            channel.users.append(user)
            db.session.add(channel)
            db.session.commit()

    @staticmethod
    def part_channel(channel_name, user):
        channel = Channel.find(channel_name)
        if user in channel.users:
            channel.users.remove(user)
            db.session.add(channel)
            db.session.commit()
        else:
            raise NotChannelMember()

    @staticmethod
    def send(message):
        # Eventually, we will only support JSON messages
        m = json.dumps(marshal(message, message_marshal))
        for user in message.channel.users:
            if user.username in Router.user_to_socket:
                for socket in Router.user_to_socket[user.username]:
                    try:
                        socket.send(m)
                    except:
                        Router.user_to_socket[user.username].remove(socket)

    @staticmethod
    def get_messages(channel_name, id_from=None, id_to=None):
        channel = Channel.find(channel_name)
        q = channel.messages

        if id_from != None:
            q = q.filter(Message.id > Message.query.filter_by(uuid=id_from).one().id)
        if id_to != None:
            q = q.filter(Message.id < Message.query.filter_by(uuid=id_to).one().id)

        return q.all()

    @staticmethod
    def delete_channel(channel_name, user):
        channel = Channel.find(channel_name)
        db.session.delete(channel)
        db.session.commit()


@authenticate
def ws_register(socket):
    username = request.user.username
    if username not in Router.user_to_socket:
        Router.user_to_socket[username] = []
    Router.user_to_socket[username].append(socket)
    while socket.connected:
        gevent.sleep(0.1)

    Router.user_to_socket[username].remove(socket)
