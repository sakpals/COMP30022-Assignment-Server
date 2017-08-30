from db import db
from datetime import datetime
from common.randomstring import generate as rs_generate

class FriendshipRequest(db.Model):
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
