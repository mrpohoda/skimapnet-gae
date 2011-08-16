# -*- coding: utf-8 -*-
"""skimapnet KML API"""


from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util
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


class UpdateFormHandler(BaseHandler):
    """View to upload a new version of KML data."""
    
    def get(self):
        self.render_template('update.html', {})


def main():
    """Bootstrap."""
    
    routes = [(r'/bounds/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/', ApiHandler),
              (r'/update/', UpdateFormHandler)]
    
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
