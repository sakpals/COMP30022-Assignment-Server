from geographiclib.geodesic import Geodesic

from db import db

class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref("location", uselist=False))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def vector_to(self, target):
        d = Geodesic.WGS84.Inverse(self.lat, self.lon, target.lat, target.lon)
        return {'distance': d['s12'], 'direction': d['azi1']}
