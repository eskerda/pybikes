# -*- coding: utf-8 -*-
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

import shapely.geometry as geometry

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class CompartiBike(BikeShareSystem):

    # Please note company is not provided by this class and should be
    # added on the metadata JSON, as CompartiBike implementation is
    # generic for different systems
    meta = {
        'system': 'CompartiBike'
    }

    def __init__(self, tag, meta, feed_url, bounding_box=None):
        super(CompartiBike, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.bounding_box = None
        if bounding_box:
            self.bounding_box = geometry.box(bounding_box[0][0],
                                             bounding_box[0][1],
                                             bounding_box[1][0],
                                             bounding_box[1][1])

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        """ Looks like:
       {
           u'number_right_slots':7,
           u'status':u'Ativa',
           u'station_number':1,
           u'password':None,
           u'description':None,
           u'total_bikes':None,
           u'created_at':u'2013-10-03T02:37:48-03:00',
           u'available_slots_size':10,
           u'updated_at':u'2014-06-27T15:11:21-03:00',
           u'id':7,
           u'status_to_human':u'Ativa',
           u'bikes':[...],
           u'number_left_slots':6,
           u'address':u'25.12.135.240',
           u'unavailable_slots_size':0,
           u'type_station':u'with_slots',
           u'mapX':None,
           u'mapY':None,
           u'googleMapY':u'-49.630102',
           u'googleMapX':u'-23.052386',
           u'name':u'Lago'
        }
        """

        data = json.loads(scraper.request(self.feed_url))

        for station in data:
            # Skip "Loldesign" stations
            if station['googleMapY'] == "" or station['googleMapX'] == "":
                continue

            longitude = float(station['googleMapY'])
            latitude = float(station['googleMapX'])

            # Skip "test" stations
            if self.bounding_box:
                point = geometry.Point(longitude, latitude)
                if not self.bounding_box.contains(point):
                    continue

            name = station['name']
            free = int(station['available_slots_size'])
            bikes = int(station['unavailable_slots_size'])

            extra = {
                'uid': int(station['id']),
                'open': station['status'] == 'Ativa',
                'number': int(station['station_number']),
                'bike_uids': [bike['id'] for bike in station['bikes']]

            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
