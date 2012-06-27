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

from datetime import datetime
import json

from utils import PyBikesScrapper

__author__ = "eskerda (eskerda@gmail.com)"
__version__ = "2.0"
__copyright__ = "Copyright (c) 2010-2012 eskerda"
__license__ = "AGPL"

__all__ = ['BikeShareStationEncoder', 'BikeShareStation', 'BikeShareSystem' ]


class BikeShareStationEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj.__dict__

class BikeShareStation(object):
    """A base class to name a bike sharing Station. It can be:
        - Specific (cities):
            - BicingStation, VelibStation, ...
        - General (companies):
            - JCDecauxStation, ClearChannelStation
    """

    def __init__(self, id, timestamp = datetime.utcnow() ):

        self.id = id
        self.name = None
        self.latitude = None
        self.longitude = None
        self.bikes = None
        self.free = None
        self.timestamp = timestamp     # Store timestamp in UTC!

    def update(self):
        """ Base update method for BikeShareStation, any subclass can
            override this method, and should/could call it from inside
        """
        self.timestamp = datetime.utcnow()

    def to_json(self, **args):
        """ Dump a json string using the BikeShareStationEncoder with a
            set of default options
        """
        if 'cls' not in args:   # Set defaults here
            args['cls'] = BikeShareStationEncoder

        return json.dumps(self, **args)

class BikeShareSystem(object):
    """A base class to name a bike sharing System. It can be:
        - Specific (cities):
            - Bicing, Velib, ...
        - General (companies):
            - JCDecaux, ClearChannel
        At the same time, these classes can extend their base class,
        for example, Velib extends JCDecaux extends BikeShareSystem.

        This class might or not have METADATA assigned, usually intended
        for specific cases. This METADATA is dict / json formatted.
    """

    tag = None

    meta = {
        'name' : None,
        'city' : None,
        'country' : None,
        'latitude' : None,
        'longitude' : None,
        'company' : None
    }

    sync = True

    stations = []

    def __init__(self):

        self.scrapper = PyBikesScrapper()

    def __str__(self):

        base = """--- {name} ---
Uname: {uname}
City: {city}
Country: {country}
LatLng: {latitude} / {longitude}
Company: {company}
"""
        return base.format(
                name = self.meta.get('name'),
                city = self.meta.get('city'),
                country = self.meta.get('country'),
                latitude = self.meta.get('latitude'),
                longitude = self.meta.get('longitude'),
                company = self.meta.get('company'),
                uname = self.tag
            )
