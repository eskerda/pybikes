# -*- coding: utf-8 -*-
# Copyright (C) 2024, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import csv
from io import StringIO

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


class LastenVelo(Bounded, BikeShareSystem):

    def __init__(self, tag, meta, feed_url, bbox=None):
        super(LastenVelo, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = scraper.request(self.feed_url)
        reader = csv.reader(StringIO(data))
        headers = next(reader, None)

        stations = []

        for row in reader:
            station = LastenVeloStation(* row)
            stations.append(station)

        self.stations = stations



class LastenVeloStation(BikeShareStation):

    def __init__(
        self,
        utc_timestamp,
        human_timestamp,
        bikeid,
        latitude,
        longitude,
        status,
        last_return_timestamp,
        name,
        subname,
        info,
        booking_url,
        osm_url,
    ):
        super(LastenVeloStation, self).__init__()

        self.name = ' - '.join(filter(None, [name, subname]))
        self.latitude = float(latitude)
        self.longitude = float(longitude)

        # every station is 1 bike. Set bikes to 1 only if the bike is available
        self.bikes = 1 if status == 'available' else 0

        self.extra = {
            'uid': bikeid,
            'status': status,
            'rental_uris': {'web': booking_url},
            'last_updated': human_timestamp,
            'bike_type': info,
        }
