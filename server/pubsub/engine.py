import json
import gevent
from flask import Blueprint, request
from flask_sockets import Sockets
from uuid import uuid4

from common.auth import authenticate
from errors import *
from db import db

ws = Blueprint('ws', __name__)

channel_members = db.Table('pubsub_channel_members',
    db.Column('channel_id', db.Integer, db.ForeignKey('pubsub_channel.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

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

    @staticmethod
    def new(channel, user, msg_type, msg_data):

        msg = Message()
        msg.channel_id = channel.id
        msg.user_id = user.id
        msg.type = msg_type

        try:
            json.loads(msg_data)
            msg.data = msg_data
        except:
            raise InvalidJSON()

        msg.channel = channel
        msg.user = user

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

    def to_string(self):
        obj = {
            'channel': self.channel.name,
            'user': self.user.username,
            'type': self.type,
            'data': json.loads(self.data)
        }

        if self.channel.persistent:
            obj['id'] = self.uuid
            obj['prev'] = self.prev_uuid
            obj['next'] = self.next_uuid

        return json.dumps(obj)

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
        m = message.to_string()
        for user in message.channel.users:
            if user.username in Router.user_to_socket:
                for socket in Router.user_to_socket[user.username]:
                    try:
                        socket.send(m)
                    except:
                        Router.user_to_socket[user.username].remove(socket)

    @staticmethod
    def delete_channel(channel_name, user):
        channel = Channel.find(channel_name)
        db.session.delete(channel)
        db.session.commit()


@ws.route('/sync')
@authenticate
def echo_socket(socket):
    username = request.user.username
    if username not in Router.user_to_socket:
        Router.user_to_socket[username] = []
    Router.user_to_socket[username].append(socket)
    while not socket.closed:
        gevent.sleep(0.1)

    Router.user_to_socket[username].remove(socket)
