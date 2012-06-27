# -*- coding: utf-8 -*-
"""
Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import re

from BeautifulSoup import BeautifulSoup

from base import BikeShareSystem, BikeShareStation
import utils

__all__ = ['BCycleSystem', 'BCycleStation']

LAT_LNG_RGX = "var\ point\ =\ new\ google.maps.LatLng\(([+-]?\\d*\\.\\d+)(?![-+0-9\\.])\,\ ([+-]?\\d*\\.\\d+)(?![-+0-9\\.])\)"
DATA_RGX = "var\ marker\ =\ new\ createMarker\(point\,(.*?)\,\ icon\,\ back\)"


BCYCLE_SYSTEMS = {
    'boulder': {
        'system': 'boulder',
        'tag': 'boulder_bcycle',
        'meta': {
            'name': 'Boulder B-Cycle',
            'city': 'Boulder, CO',
            'country': 'USA',
            'latitude': 40.0149856,
            'longitude': -105.2705455
            }
    }
    ,'chicago': {
        'system': 'chicago',
        'tag': 'chicago_bcycle',
        'meta': {
            'name': 'Chicago Bikes',
            'city': 'Chicago, IL',
            'country': 'USA',
            'latitude': 41.8781136,
            'longitude': -87.6297981
            }
    }
    ,'broward': {
        'system': 'broward',
        'tag': 'broward_bcycle',
        'meta': {
            'name': 'Broward B-Cycle',
            'city': 'Broward, FL',
            'country': 'USA',
            'latitude': 26.190096,
            'longitude': -80.365864
            }
    }
    ,'denver': {
        'system': 'denver',
        'tag': 'denver_bcycle',
        'meta': {
            'name': 'Denver Bikes',
            'city': 'Denver, CO',
            'country': 'USA',
            'latitude': 39.737567,
            'longitude': -104.984717
            }
    }
    ,'des_moines': {
        'system': 'desmoines',
        'tag': 'des_moines_bcycle',
        'meta': {
            'name': 'Des Moines B-cycle',
            'city': 'Des Moines, IA',
            'country': 'USA',
            'latitude': 41.6005448,
            'longitude': -93.6091063
            }
    }
}

class BCycleError(Exception):
    def __init__(self, msg):
            self.msg = msg

    def __repr__(self):
            return self.msg
    __str__ = __repr__


class BCycleSystem(BikeShareSystem):

    feed_url = "http://{system}.bcycle.com"
    sync = True

    meta = dict(BikeShareSystem.meta, 
      **{ 'system': 'B-cycle',
          'company': [ 'Trek Bicycle Corporation'
                     ,'Humana'
                     ,'Crispin Porter + Bogusky' ]
        })

    def update(self):

        html_data = self.scrapper.request(self.feed_url).read()

        geopoints = re.findall(LAT_LNG_RGX, html_data)
        puzzle = re.findall(DATA_RGX, html_data)

        for index, fuzzle in enumerate(puzzle):
            
            station = BCycleStation(index)
            station.latitude = float(geopoints[index][0])
            station.longitude = float(geopoints[index][1])
            station.from_html(fuzzle)

            self.stations.append(station)


class BCycleStation(BikeShareStation):

    def from_html(self, fuzzle):
        """ Take a good look at this fuzzle:
            var point = new google.maps.LatLng(41.86727, -87.61527);
            var marker = new createMarker(
                point,                       .--- Fuzzle
                "<div class='location'>      '    
                    <strong>Museum Campus</strong><br />
                    1200 S Lakeshore Drive<br />
                    Chicago, IL 60605
                </div>
                <div class='avail'>Bikes available: <strong>0</strong><br />Docks available: <strong>21</strong></div><br/>
                ", icon, back);
            Now, do something about it
        """

        soup = BeautifulSoup(fuzzle)
        self.name = str(soup.contents[1].contents[0].contents[0])
        self.bikes = int(soup.contents[2].contents[1].contents[0])
        self.free = int(soup.contents[2].contents[4].contents[0])

        self.extra = {'address' : "%s - %s" % (
                        str(soup.contents[1].contents[2]),
                        str(soup.contents[1].contents[4]))}

def system(key):
    if key not in BCYCLE_SYSTEMS:
        raise BCycleError('Invalid system or not implemented')
    
    sys_data = BCYCLE_SYSTEMS.get(key)
    
    r = BCycleSystem()
    r.feed_url = BCycleSystem.feed_url.format(system = sys_data.get('system'))
    r.tag = sys_data.get('tag')
    r.meta = dict( BCycleSystem.meta, **sys_data.get('meta'))

    return r