# -*- coding: utf-8 -*-


from collections import deque
from google.appengine.ext import db
from model import Track, TrackPoint


class ImportLoader(object):
    
    def load(self):
        raise NotImplementedError()
    

class TracksImportLoader(ImportLoader):
    
    def _get_centroid(self, points):
        """Centroid ... https://secure.wikimedia.org/wikipedia/en/wiki/Polygon#Area_and_centroid"""
        
        points = map(lambda x: (float(x[0]), float(x[1])), points)
        
        if len(points) == 1:
            # single point (wtf? but... whatever...)
            return points[0] 
        if len(points) == 2:
            # line
            return (
                (points[0][0] + points[1][0]) / 2,
                (points[0][1] + points[1][1]) / 2
            )
        
        shifted_points = deque(points)
        shifted_points.rotate(-1)
        
        points = zip(points, list(shifted_points))
        
        area_sum = 0
        centroid_x_sum = 0
        centroid_y_sum = 0
        
        for (x1, y1), (x2, y2) in points:
            area_sum += (x1 * y2 - x2 * y1)
            tmp = (x1 * y2 - x2 * y1)
            centroid_x_sum += (x1 + x2) * tmp
            centroid_y_sum += (y1 + y2) * tmp
        
        area = abs(0.5 * area_sum)
        tmp = (1/(6 * area))
        
        return (
            tmp * centroid_x_sum,
            tmp * centroid_y_sum
        )
    
    def load(self, tracks):
        for line in tracks:
            track = Track(color=line['color'])
            track.put()

            points = []
            for i, coords in enumerate(line['coords']):
                point = TrackPoint(order=i, track=track, location=db.GeoPt(*coords))
                point.update_location()
                points.append(point)
            db.put(points)
            
            track.location = db.GeoPt(*self._get_centroid(line['coords']))
            track.update_location()
            track.put()
            

