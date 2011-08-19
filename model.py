# -*- coding: utf-8 -*-


from geo.geomodel import GeoModel
from google.appengine.ext import db



class TravelAgency(db.Model):
    name = db.StringProperty(required=True)
    
    
class Track(db.Model):
    color = db.StringProperty(required=True)


class Point(GeoModel):
    pass


class Hotel(Point):
    category = db.CategoryProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.StringProperty()
    rooms_count = db.IntegerProperty()
    person_limit_min = db.IntegerProperty()
    person_limit_max = db.IntegerProperty()
    price_min = db.IntegerProperty()
    currency = db.CategoryProperty()
    link = db.LinkProperty()
