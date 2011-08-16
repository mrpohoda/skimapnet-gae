# -*- coding: utf-8 -*-


from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template, util
from models import TravelAgency
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
        self.redirect('/update/')
        
        
class UpdateFormHandler(BaseHandler):
    """View to upload a new version of KML/CVS data."""
    
    def get(self):
        self.render_template('update.html', {
            'travel_agencies': list(TravelAgency.all().order('name')),
        })
        
    def post(self):
        print self.request.get('img')


def main():
    """Bootstrap."""
    
    routes = [(r'/bounds/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/', ApiHandler),
              (r'/update/', UpdateFormHandler),
              (r'/travel-agency/([\w\-]+)/', TravelAgencyHandler)]
    
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
