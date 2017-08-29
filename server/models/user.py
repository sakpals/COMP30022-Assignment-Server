import random, string

from bcrypt import hashpw, gensalt
from datetime import datetime
from db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(256))
    description = db.Column(db.String(4096))
    image_url = db.Column(db.String(512))
    tokens = db.relationship('Token', backref=db.backref('user', lazy='joined'),
                                lazy='dynamic')

    def __init__(self, _u, _p, _d, _i):
        self.username = _u
        self.password = hashpw(_p.encode('utf8'), gensalt(14))
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

    @staticmethod
    def from_args(args):
        return User(args["username"], args["password"], args["description"], args["avatar_url"])

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_string = db.Column(db.String(128)) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_use = db.Column(db.DateTime)

    def __init__(self):
        self.token_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(128)])
        self.last_use = datetime.utcnow()

    def __str__(self):
        return self.token_string

    __repr__ = __str__
