# -*- coding: utf-8 -*-


from StringIO import StringIO
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template, util
from models import TravelAgency
import os
import re
import xml.etree.ElementTree as ElementTree


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
        })
        

class UpdateHandler(BaseHandler):
    """View handling upload of a new version of KML/CVS data."""
    
    def _update_ski_tracks(self, file_contents):
        print 'debug'
        
        # parse KML
        ns = 'http://www.opengis.net/kml/2.2'
        context = iter(ElementTree.iterparse(StringIO(file_contents), events=('start', 'end')))
        _, root = context.next()
        
        style_maps = {}
        styles = {}
        lines = []
        for event, elem in context:
            if event == 'end':
                if elem.tag == ('{%s}StyleMap' % ns):
                    # style mapping
                    for pair in elem.findall('.//{%s}Pair' % ns):
                        if pair.find('{%s}key' % ns).text == 'normal':
                            style_maps[elem.attrib['id']] = pair.find('{%s}styleUrl' % ns).text.lstrip('#')
                            
                elif elem.tag == ('{%s}Style' % ns):
                    styles[elem.attrib['id']] = elem.find('{%s}LineStyle/{%s}color' % (ns, ns)).text
                    
                elif elem.tag == ('{%s}Placemark' % ns):
                    style = elem.find('{%s}styleUrl' % ns).text.lstrip('#')
                    for line in elem.findall('.//{%s}LineString' % ns):
                        lines.append({
                            'coords': line.find('{%s}coordinates' % ns).text.strip(),
                            'style': style,
                        })
        root.clear()
        
        # process line by line and prepare for saving
        coords_sep_re = re.compile(r'\s+')
        for line in lines:
            # apply styles
            if line['style'] in styles:
                line['color'] = styles[line['style']]
            elif line['style'] in style_maps:
                line['color'] = styles[style_maps[line['style']]]
            del line['style']
            
            # normalize coords
            line['coords'] = [coord.split(',')[:2] for coord in coords_sep_re.split(line['coords'])]
            
        # TODO save
        print lines
    
    def _update_hotels(self, file_contents, travel_agency_id):
        pass
    
    def post(self, action):
        if action == 'ski-tracks':
            self._update_ski_tracks(self.request.get('ski_tracks_kml'))
        elif action == 'hotels':
            self._update_hotels(self.request.get('hotels_cvs'), self.request.get('hotels_travel_agency'))
        #self.redirect('/admin/')


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
