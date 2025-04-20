# -*- coding: utf-8 -*-
# Copyright (C) 2010-2025, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import hashlib

from datetime import datetime
from dataclasses import dataclass

from pybikes.compat import utcnow


class GeneralPurposeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, BikeShareSystem):
            return obj.to_dict()
        elif isinstance(obj, BikeShareStation):
            return obj.to_dict()
        elif isinstance(obj, Vehicle):
            return obj.to_dict()
        return super().default(obj)


class BikeShareStation(object):
    """A base class to name a bike sharing Station. It can be:
        - Specific (cities):
            - BicingStation, VelibStation, ...
        - General (companies):
            - JCDecauxStation, ClearChannelStation
    """

    def __init__(self, name = None, latitude = None, longitude = None,
                       bikes = None, free = None, extra = None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.bikes = bikes
        self.free = free
        self.timestamp = utcnow()     # Store timestamp in UTC!
        self.extra = extra or {}

    def __str__(self):
        return "--- {0} ---\n"\
               "bikes: {1}\n"\
               "free: {2}\n"\
               "latlng: {3},{4}\n"\
               "extra: {5}"\
               .format(repr(self.name), self.bikes, self.free, self.latitude, \
                       self.longitude,self.extra)

    def update(self, scraper = None):
        """ Base update method for BikeShareStation, any subclass can
            override this method, and should/could call it from inside
        """
        self.timestamp = utcnow()

    def to_dict(self):
        """ explicit obj to dict method """
        return {
            'id': self.get_hash(),
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'bikes': self.bikes,
            'free': self.free,
            'timestamp': self.timestamp,
            'extra': self.extra,
        }

    def to_json(self, **args):
        """ Dump a json string using the BikeShareStationEncoder with a
            set of default options
        """
        if 'cls' not in args:   # Set defaults here
            args['cls'] = GeneralPurposeEncoder

        return json.dumps(self, **args)

    def to_geojson(self, **args):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "name": self.name,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "bikes": self.bikes,
                "free": self.free,
                "extra": self.extra,
                "type": "station",
                # ...
            },
        }

    def get_hash(self):
        """ Return a unique hash representing this station, usually with
            latitude and longitude, since it's the only globally ready and
            reliable information about an station that defines the
            difference between one and another
        """
        str_rep = "%d,%d" % (int(self.latitude * 1E6), int(self.longitude * 1E6))
        h = hashlib.md5()
        h.update(str_rep.encode('utf-8'))
        return h.hexdigest()


class BikeShareSystem(object):
    """A base class to name a bike sharing System. It can be:
        - Specific (cities):
            - Bicing, Velib, ...
        - General (companies):
            - JCDecaux, ClearChannel
        At the same time, these classes can extend their base class,
        for example, Velib extends Smovengo extends BikeShareSystem.

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

    authed = False

    unifeed = False

    def __init__(self, tag, meta):
        self.vehicles = []
        self.stations = []

        self.tag = tag
        basemeta = dict(BikeShareSystem.meta, **self.meta)
        self.meta = dict(basemeta, **meta)
        if not self.meta['name'] and self.meta['system']:
            self.meta['name'] = self.meta['system']

    def __str__(self):
        return "tag: %s\nmeta: %s" % (self.tag, str(self.meta))

    def to_dict(self):
        """ explicit obj to dict method """

        return {
            'tag': self.tag,
            'meta': self.meta,
            'stations': [s.to_dict() for s in self.stations],
            'vehicles': [e.to_dict() for e in self.vehicles],
        }

    def to_json(self, **args):
        """ Dump a json string using the BikeShareSystemEncoder with a
            set of default options
        """
        if 'cls' not in args:   # Set defaults here
            args['cls'] = GeneralPurposeEncoder

        return json.dumps(self, **args)

    def to_geojson(self, **args):
        return {
            "type": "FeatureCollection",
            "features": [
                station.to_geojson() for station in self.stations
            ] + [
                vehicle.to_geojson() for vehicle in self.vehicles
            ],
        }


@dataclass
class VehicleType:
    # These are mostly an homonym on GBFS vehicle types.
    # You know, dead batteries sometimes leak

    # One of: human|electric|assist
    power: str
    # Name
    name: str
    # Short name
    alias: str


class VehicleTypes:
    bicycle = VehicleType(power="human", name="Humble bike", alias="bike")
    ebike = VehicleType(power="electric", name="Electric Bike", alias="ebike")
    # as in: What an ass bike
    ass_bike = VehicleType(power="assist", name="Electric Assisted Bike",
                           alias="ass_bike")
    scooter = VehicleType(power="electric", name="Scooter", alias="scooter")
    default = bicycle


class Vehicle:
    vehicle_type: VehicleType
    latitude: float
    longitude: float
    extra: dict
    timestamp: str

    def __init__(self, latitude, longitude, vehicle_type=None, extra=None,
                 system=None):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self._system = system
        self.kind = vehicle_type or VehicleTypes.default

        # Any network specific extra info that might go in here:
        # - battery level
        # - ... ?
        self.extra = extra or {}

        self.timestamp = utcnow()


    @property
    def system(self):
        if not self._system:
            # Careful, somewhat expensive
            from pybikes.utils import introspect_network
            self._system = introspect_network()
        return self._system

    @property
    def uid(self):
        return self.extra.get('uid', None)

    @property
    def hash(self):
        """ Return a unique hash representing this entity
            Try to get a uid, if that fails use lat/lng
            Add parent system tag to the mix and any other info to make it
            unique
        """
        cmps = []

        if self.system:
            cmps += [self.system.tag]

        if self.uid:
            cmps += [self.uid]
        else:
            cmps += [
                int(self.latitude * 1E6),
                int(self.longitude * 1E6),
                self.kind.alias,
            ]

        str_rep = ",".join(map(str, cmps))

        h = hashlib.md5()
        h.update(str_rep.encode('utf-8'))
        return h.hexdigest()

    def to_dict(self):
        return {
            "id": self.hash,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "kind": self.kind.alias,
            "extra": self.extra,
            "timestamp": self.timestamp,
        }

    def to_geojson(self, **args):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "id": self.hash,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "extra": self.extra,
                "type": "vehicle",
                "kind": self.kind.alias,
                # ...
            },
        }
