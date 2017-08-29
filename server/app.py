from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from resources.user import UserLogin, UserLogout, UserRegister, UserProfile 
from errors import error_list
from db import db

app = Flask(__name__)
# Store database on disk
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app, errors=error_list)

db.init_app(app)

api.add_resource(UserLogin, '/user/login')
api.add_resource(UserLogout, '/user/logout')
api.add_resource(UserRegister, '/user/register')
api.add_resource(UserProfile, '/profile/<username>')

if __name__ == '__main__':
    db.create_all(app=app)
    app.run(debug=False)
