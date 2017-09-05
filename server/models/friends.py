from db import db
from datetime import datetime
from common.randomstring import generate as rs_generate

class FriendshipRequest(db.Model):
    __tablename__ = 'friend_request'

    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime)
    token = db.Column(db.String(128))

    user_from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user_from = db.relationship("User", backref="outgoing_friend_requests", foreign_keys=[user_from_id])
    user_to = db.relationship("User", backref="incoming_friend_requests", foreign_keys=[user_to_id])

    def __init__(self, user_from, user_to):
        self.created = datetime.utcnow()
        self.token = rs_generate(128)
        self.user_from = user_from
        self.user_to = user_to

class Friendship(db.Model):
    __tablename__ = 'friend'

    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime)
    me_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    me = db.relationship("User", backref=db.backref("friends", lazy="select"), foreign_keys=[me_id])
    friend = db.relationship("User", foreign_keys=[friend_id], lazy="joined")

    def __init__(self, me, friend, time=datetime.utcnow()):
        self.me_id = me.id
        self.friend_id = friend.id
        self.created = time

    @staticmethod
    def add_friendship(friendship):
        Friendship.add_pair(friendship.me, friendship.friend)

    @staticmethod
    def add_pair(me, friend):
        time = datetime.utcnow()
        db.session.add(Friendship(me, friend, time))
        db.session.add(Friendship(friend, me, time))

    @staticmethod
    def remove_friendship(friendship):
        Friendship.remove_pair(friendship.me, friendship.friend)

    @staticmethod
    def remove_pair(me, friend):
        db.session.delete(Friendship.query.filter_by(me=me, friend=friend).one())
        db.session.delete(Friendship.query.filter_by(me=friend, friend=me).one())
