# -*- coding: utf-8 -*-
"""skimapnet KML API"""



from google.appengine.ext import webapp
from google.appengine.ext.webapp import util



class ApiHandler(webapp.RequestHandler):
    """View to handle GET KML API requests."""
    
    def get(self, *args):
        bounds = ((args[0], args[1]), (args[2], args[3]))
        
        #self.response.out.write('API.')
        print bounds



class UpdateFormHandler(webapp.RequestHandler):
    """View to upload a new version of KML data."""
    
    def get(self):
        self.response.out.write('Here be dragons.')



def main():
    """Bootstrap."""
    
    routes = [(r'/bounds/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/([\d\.\-]+)/', ApiHandler),
              (r'/', UpdateFormHandler)]
    
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)



if __name__ == '__main__':
    main()
