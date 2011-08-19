# -*- coding: utf-8 -*-


from StringIO import StringIO
import re
import xml.etree.ElementTree as ElementTree


class ImportParser(object):
    
    def __init__(self, file_contents):
        self.file_contents = file_contents
        
    def parse(self):
        raise NotImplementedError()


class TracksImportParser(ImportParser):
    
    def _normalize_coords(self, coords):
        coords = coords.split(',')[:2]
        coords.reverse() # beware to have lat/lng in the right order
        return coords
    
    def _normalize_color(self, color):
        return '#' + color[2:]
    
    def parse(self):
        # parse KML
        ns = 'http://www.opengis.net/kml/2.2'
        context = iter(ElementTree.iterparse(StringIO(self.file_contents), events=('start', 'end')))
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
        
        # process line by line and prepare for saving & then save
        coords_sep_re = re.compile(r'\s+')
        for line in lines:
            # apply styles
            if line['style'] in styles:
                line['color'] = self._normalize_color(styles[line['style']])
            elif line['style'] in style_maps:
                line['color'] = self._normalize_color(styles[style_maps[line['style']]])
            del line['style']
            
            # coords
            line['coords'] = [self._normalize_coords(coords) for coords in coords_sep_re.split(line['coords'])]
            
            yield line
    

class HotelImportParser(ImportParser):
    pass
