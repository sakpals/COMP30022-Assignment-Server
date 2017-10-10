from flask_restful import Resource, reqparse, fields, marshal_with
from datetime import datetime
from flask import request

from common.auth import authenticate
from models.location import Location
from models.user import User
from errors import *
from db import db

class LocationResource(Resource):

    @authenticate
    def post(self, username):
        target = User.find(username)

        # Currently only authorised to update your own location
        if request.user != target:
            raise UnauthorisedError()

        parser = reqparse.RequestParser()
        parser.add_argument('lat', required=True, type=float, help='lat required')
        parser.add_argument('lon', required=True, type=float, help='lon required')
        args = parser.parse_args()

        location = target.location
        if location == None:
            location = Location()
        location.lat = args.lat
        location.lon = args.lon
        location.user_id = target.id
        location.updated = datetime.utcnow()
        db.session.add(location)
        db.session.commit()

        return {},200

    f = {
        'distance': fields.Float,
        'direction': fields.Float,
    }
    @marshal_with(f)
    @authenticate
    def get(self, username):
        user = User.find(username)

        if request.user.location == None:
            raise LocationNotStored()
        if user.location == None:
            raise LocationNotStored()

        return request.user.location.vector_to(user.location)

