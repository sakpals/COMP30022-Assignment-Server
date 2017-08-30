from flask_restful import fields
from bcrypt import hashpw, gensalt
from datetime import datetime

from common.randomstring import generate as rs_generate
from errors import NotFoundError
from db import db

# Defines the fields we want to return on get. Obviously we don't want
# to return users passwords on any request
profile_fields = {
    'username': fields.String,
    'description': fields.String,
    'avatar_url': fields.String,
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    hashed_password = db.Column(db.String(256))
    description = db.Column(db.String(4096))
    image_url = db.Column(db.String(512))
    tokens = db.relationship('Token', backref=db.backref('user', lazy='joined'),
                                lazy='dynamic')

    def __init__(self, _u, _p, _d, _i):
        self.username = _u
        self.password = _p
        self.description = _d
        self.image_url = _i

    def __repr__(self):
        return '<User %r>' % self.username

    def add_token(self):
        token = Token()
        self.tokens.append(token)
        db.session.add(token)
        db.session.add(self)
        db.session.commit()
        return token

    def login(self, password):
        if(self.password == hashpw(password.encode('utf8'), self.password)):
            return self.add_token().token_string
        else:
            return None

    @property
    def password(self):
        """I'm the 'x' property."""
        return self.hashed_password

    @password.setter
    def password(self, value):
        self.hashed_password = hashpw(value.encode('utf8'), gensalt(14))

    @staticmethod
    def from_args(args):
        return User(
                args["username"],
                args["password"],
                args["description"],
                args["avatar_url"]
                )

    @staticmethod
    def find(username, fail_not_found=True):
        user = User.query.filter_by(username=username).first()
        if user == None and fail_not_found:
            raise NotFoundError()
        else:
            return user

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_string = db.Column(db.String(128), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_use = db.Column(db.DateTime)

    def __init__(self):
        self.token_string = rs_generate(128)
        self.last_use = datetime.utcnow()

    def __str__(self):
        return self.token_string

    __repr__ = __str__
