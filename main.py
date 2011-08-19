# -*- coding: utf-8 -*-


from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template, util
from model import TravelAgency, Track, Point, Hotel
from parsing import TracksImportParser
import os


class BaseHandler(webapp.RequestHandler):
    
    def render_template(self, file, params={}):
        path = os.path.join(os.path.dirname(__file__), 'templates', file)
        self.response.out.write(template.render(path, params))


class ApiHandler(BaseHandler):
    """View to handle GET KML API requests."""
    
    def get(self, *args):
        bounds = ((args[0], args[1]), (args[2], args[3]))
        
        #self.response.out.write('API.')
        print bounds


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
            'points_count': Point.all().count(),
            'hotels_count': Hotel.all().count(),
        })
        

class UpdateHandler(BaseHandler):
    """View handling upload of a new version of KML/CVS data."""
    
    def _update_ski_tracks(self, file_contents):
        # delete all existing data
        db.delete(Track.all())
        db.delete(Point.all())
        
        # save new data
        for line in TracksImportParser(file_contents).parse():
            track = Track(color=line['color'])
            track.put()

            points = []
            for coords in line['coords']:
                coords.reverse() # to have lat/lng in the right order
                point = Point(parent=track, location=db.GeoPt(*coords))
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
    
    routes = [(r'/bounds/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/', ApiHandler),
              (r'/admin/', AdminPageHandler),
              (r'/update/([\w\-]+)/', UpdateHandler),
              (r'/travel-agency/([\w\-]+)/', TravelAgencyHandler)]
    
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
