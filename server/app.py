from flask import Flask, Blueprint
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_uwsgi_websocket import GeventWebSocket

from resources.friends import *
from resources.user import *
from resources.location import *
from resources.pubsub import *
from resources.image import *
from pubsub.engine import ws_register
from errors import error_list
from db import db

API_VERSION="1"

app = Flask(__name__)
# load config from disk
app.config.from_pyfile('config.py')
app.config.from_envvar('CHLORINE_CONFIG', silent=True)

api_bp = Blueprint('api', __name__)

api = Api(api_bp, errors=error_list)
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserLogout, '/user/logout')
api.add_resource(UserRegister, '/user/register')
api.add_resource(UserProfile, '/profile/<username>')
api.add_resource(SelfProfile, '/profile')

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

api.add_resource(ImageUpload, '/image')
api.add_resource(ImageView, '/image/<image_id>')

db.init_app(app)
db.create_all(app=app)

# Leaving this here for eventual API versioning.
# app.register_blueprint(api_bp, url_prefix='/api/v%s' % API_VERSION)
app.register_blueprint(api_bp)

## patch_request wraps a websocket function, patching Flask.request
def patch_request(fn):
    def wrap(ws):
        with app.request_context(ws.environ):
            fn(ws)
    return wrap

# Setup websocket route
websocket = GeventWebSocket(app)
ws_register = patch_request(ws_register)
websocket.route('/sync')(ws_register)

if __name__ == "__main__":
    logfile = app.config['LOGFILE']
    params = {'gevent': 100, 'logto': logfile, 'reuse-port': True}
    app.run(**params)
