from flask import Flask, Blueprint
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from resources.friends import *
from resources.user import *
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

db.init_app(app)
db.create_all(app=app)

# Leaving this here for eventual API versioning.
# app.register_blueprint(api_bp, url_prefix='/api/v%s' % API_VERSION)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run()
