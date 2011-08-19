# -*- coding: utf-8 -*-


from django.utils import simplejson as json
from geo import geotypes
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template, util
from model import TravelAgency, Track, TrackPoint, Hotel
from parsing import TracksImportParser
import os


class BaseHandler(webapp.RequestHandler):
    
    def render_template(self, file, params={}):
        path = os.path.join(os.path.dirname(__file__), 'templates', file)
        self.response.out.write(template.render(path, params))


class ApiHandler(BaseHandler):
    
    def render_as_json(self, contents):
        #self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(json.dumps(contents))
    

class TracksHandler(ApiHandler):
    """View to provide tracks."""
    
    RESPONSE_SIZE = 1000
    
    def get(self, *args):
        args = [float(x) for x in args]
        bounds = geotypes.Box(*args)
        
        tracks = {}
        for point in TrackPoint.bounding_box_fetch(TrackPoint.all().order('order'), bounds, max_results=TracksHandler.RESPONSE_SIZE):
            track_id = point.track.key().id()
            if track_id not in tracks:
                tracks[track_id] = {'id': track_id, 'color': point.track.color, 'points': []}
            tracks[track_id]['points'].append({'lat': point.location.lat, 'lng': point.location.lon, 'order': point.order})
        
        self.render_as_json({
            'bounds': args,
            'tracks': tracks.values(),
        })


class HotelsHandler(ApiHandler):
    """View to provide hotels."""
    
    def get(self, *args):
        pass


class TravelAgencyHandler(BaseHandler):
    """Travel agency management."""
    
    def _create(self):
        agency = TravelAgency(name=self.request.get('name'))
        agency.put()
    
    def _delete(self):
        keys = [db.Key.from_path('TravelAgency', int(id)) for id in self.request.get_all('id')]
        db.delete(keys)
        # TODO delete also all hotels
    
    def post(self, action):
        getattr(self, '_' + action)()
        self.redirect('/admin/')
        
        
class AdminPageHandler(BaseHandler):
    """View to upload a new version of KML/CVS data."""
    
    def get(self):
        self.render_template('admin.html', {
            'travel_agencies': list(TravelAgency.all().order('name')),
            'tracks_count': Track.all().count(),
            'points_count': TrackPoint.all().count(),
            'hotels_count': Hotel.all().count(),
        })
        

class UpdateHandler(BaseHandler):
    """View handling upload of a new version of KML/CVS data."""
    
    def _update_ski_tracks(self, file_contents):
        # delete all existing data
        db.delete(TrackPoint.all())
        db.delete(Track.all())
        
        # save new data
        for line in TracksImportParser(file_contents).parse():
            track = Track(color=line['color'])
            track.put()

            points = []
            for i, coords in enumerate(line['coords']):
                point = TrackPoint(order=i, track=track, location=db.GeoPt(*coords))
                point.update_location()
                points.append(point)
            db.put(points)
    
    def _update_hotels(self, file_contents, travel_agency_id):
        pass
    
    def post(self, action):
        if action == 'ski-tracks':
            self._update_ski_tracks(self.request.get('ski_tracks_kml'))
        elif action == 'hotels':
            self._update_hotels(self.request.get('hotels_cvs'), self.request.get('hotels_travel_agency'))
        self.redirect('/admin/')


def main():
    """Bootstrap."""
    
    routes = [(r'/tracks/bounds/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/', TracksHandler),
              (r'/hotels/bounds/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/', HotelsHandler),
              (r'/admin/', AdminPageHandler),
              (r'/update/([\w\-]+)/', UpdateHandler),
              (r'/travel-agency/([\w\-]+)/', TravelAgencyHandler)]
    
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
