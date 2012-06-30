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

    def __init__(self, tag, meta, system = None, feed_url = None):
        super( BCycleSystem, self).__init__()
        self.tag = tag
        if feed_url is not None:
            self.feed_url = feed_url
        else:
            self.feed_url = BCycleSystem.feed_url.format(system =  system)
        self.meta = dict(BCycleSystem.meta, **meta)

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