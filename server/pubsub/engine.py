import gevent
from flask import Blueprint, request
from flask_sockets import Sockets

from common.auth import authenticate
from db import db

ws = Blueprint('ws', __name__)

channel_members = db.Table('pubsub_channel_members',
    db.Column('channel_id', db.Integer, db.ForeignKey('pubsub_channel.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Channel(db.Model):
    __tablename__ = 'pubsub_channel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
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
    def new_channel(channel_name, user):
        channel = Channel()
        channel.name = channel_name
        channel.users.append(user)
        db.session.add(channel)
        db.session.commit()

    @staticmethod
    def join_channel(channel_name, user):
        channel = Channel.find(channel_name)
        channel.users.append(user)
        db.session.add(channel)
        db.session.commit()

    @staticmethod
    def part_channel(channel_name, user):
        channel = Channel.find(channel_name)
        channel.users.remove(user)
        db.session.add(channel)
        db.session.commit()

    @staticmethod
    def message_channel(channel_name, message):
        # Eventually, we will only support JSON messages
        channel = Channel.find(channel_name)
        for user in channel.users:
            Router.user_to_socket[user.username].send(str(message))

    @staticmethod
    def delete_channel(channel_name, user):
        channel = Channel.find(channel_name)
        db.session.delete(channel)
        db.session.commit()

@ws.route('/sync')
@authenticate
def echo_socket(socket):
    username = request.user.username
    Router.user_to_socket[username] = socket
    while not socket.closed:
        gevent.sleep(0.1)

    Router.user_to_socket[username] = None
