from flask import Flask, Blueprint
from flask_restful import Api
from flask_sockets import Sockets
from flask_sqlalchemy import SQLAlchemy

from resources.friends import *
from resources.user import *
from resources.location import *
from resources.pubsub import *
from pubsub.engine import ws
from errors import error_list
from db import db

API_VERSION="1"

app = Flask(__name__)
# Store database on disk
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api_bp = Blueprint('api', __name__)

api = Api(api_bp, errors=error_list)
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserLogout, '/user/logout')
api.add_resource(UserRegister, '/user/register')
api.add_resource(UserProfile, '/profile/<username>')

api.add_resource(FriendList, '/friends')
api.add_resource(FriendAdd, '/friends/add/<username>')
api.add_resource(FriendAccept, '/friends/accept/<request_token>')
api.add_resource(FriendRemove, '/friends/remove/<username>')
api.add_resource(FriendIncomingRequests, '/friends/requests/in')
api.add_resource(FriendOutgoingRequests, '/friends/requests/out')

api.add_resource(LocationResource, '/location/<username>')

api.add_resource(ChannelCRUD, '/channel/<channel_name>')
api.add_resource(ChannelJoin, '/channel/<channel_name>/join')
api.add_resource(ChannelPart, '/channel/<channel_name>/leave')
api.add_resource(ChannelMessage, '/channel/<channel_name>/message')

db.init_app(app)
db.create_all(app=app)

sockets = Sockets(app)
# Leaving this here for eventual API versioning.
# sockets.register_blueprint(ws, url_prefix='/api/v%s' % API_VERSION)
# app.register_blueprint(api_bp, url_prefix='/api/v%s' % API_VERSION)
sockets.register_blueprint(ws)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
