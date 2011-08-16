# -*- coding: utf-8 -*-


from google.appengine.ext import db


class TravelAgency(db.Model):
    name = db.StringProperty(required=True)
    