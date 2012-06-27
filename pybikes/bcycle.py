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
"""
                                        O_
   AWESOMENESS TIME  THIS WAY          /  >
                ↓                     -  >   ^\
                                     /   >  ^ /   
                                    (O)  > ^ /   / / /  
       _____                        |            \\|//
      /  __ \                      _/      /     / _/
     /  /  | |                    /       /     / /
   _/  |___/ /                  _/      ------_/ / 
 ==_|  \____/                  _/       /  ______/
     \   \                 __/           |\
      |   \_          ____/              / \      _                    
       \    \________/                  |\  \----/_V
        \_                              / \_______ V
          \__                /       \ /          V
             \               \        \
              \______         \_       \
                     \__________\_      \ 
                        /    /    \_    | 
                       |   _/       \   |
                      /  _/          \  |
                     |  /            |  |
                     \  \__          |   \__
                     /\____=\       /\_____=\
"""
bcycle_systems = [
    {
        'clsName': 'Boulder',
        'system': 'boulder',
        'tag': 'boulder_bcycle',
        'meta': {
            'name': 'Boulder B-Cycle',
            'city': 'Boulder, CO',
            'country': 'USA',
            'latitude': 40.0149856,
            'longitude': -105.2705455
            }
    },
    {
        'clsName': 'Chicago',
        'system': 'chicago',
        'tag': 'chicago_bcycle',
        'meta': {
            'name': 'Chicago Bikes',
            'city': 'Chicago, IL',
            'country': 'USA',
            'latitude': 41.8781136,
            'longitude': -87.6297981
            }
    },
    {
        'clsName': 'Broward',
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
    ,{
        'clsName': 'Denver',
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
]

for system in bcycle_systems:
    vars()[system['clsName']] = type(
            system['clsName'],
            (BCycleSystem, ),
            {
                'tag': system['tag'],
                'feed_url': BCycleSystem.feed_url
                                        .format(
                                            system = system['system']),
                'meta': dict( BikeShareSystem.meta, 
                              **system['meta'])
            })
    __all__.append(system['clsName'])