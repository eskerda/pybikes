# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from lxml import etree

from shapely.geometry import Point, box

from .base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper
from pybikes.contrib import TSTCache

__all__ = ['Nextbike', 'NextbikeStation']

BASE_URL = 'https://{hostname}/maps/nextbike-live.xml?domains={domain}&get_biketypes=1'  # NOQA

# Since most networks share the same hostname, there's no need to keep hitting
# the endpoint on the same urls. This caches the feed for 60s
cache = TSTCache(delta=60)


class Nextbike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'Nextbike',
        'company': 'Nextbike GmbH'
    }

    def __init__(self, tag, meta, domain, city_uid, hostname='nextbike.net',
                 bbox=None):
        super(Nextbike, self).__init__(tag, meta)
        self.url = BASE_URL.format(hostname=hostname, domain=domain)
        self.domain = domain
        self.uid = city_uid
        self.bbox = None
        if bbox:
            self.bbox = box(bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1])

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper(cache)
        domain_xml = etree.fromstring(
            scraper.request(self.url).encode('utf-8')
        )
        places = domain_xml.xpath(
            '/markers/country/city[@uid="{uid}"]/place'.format(uid=self.uid)
        )
        # We want to raise an error if a uid is invalid, right?
        assert places, "Not found: uid {!r}, domain {!r}, url {}".format(
            self.uid, self.domain, self.url
        )
        self.stations = map(NextbikeStation, self.filter_stations(places))

    def filter_stations(self, places):
        for place in places:
            # TODO: For now we are not going to track bikes roaming around
            if place.attrib.get('bike', '') == '1':
                continue
            # Some networks include testing stations that are outside of the
            # system. On these cases, a bounding box can be provided to filter
            # them out.
            if self.bbox:
                lat = float(place.attrib['lat'])
                lng = float(place.attrib['lng'])
                coord = Point(lng, lat)
                if not self.bbox.contains(coord):
                    continue
            yield place


class NextbikeStation(BikeShareStation):
    def __init__(self, place):
        super(NextbikeStation, self).__init__()
        self.name = place.attrib['name']
        self.latitude = float(place.attrib['lat'])
        self.longitude = float(place.attrib['lng'])
        self.extra = {}

        self.extra['uid'] = place.attrib['uid']
        if 'number' in place.attrib:
            self.extra['number'] = place.attrib['number']

        # Greater than 5 will appear as 5+ on that case, we set bikes
        # approximate to true, to signal that the number is not exact. Note
        # this is rather frequent case for 'bike_types' and infrequent
        # corner case for 'bikes' attribute.
        if 'bike_types' in place.attrib:
            self.bikes = 0
            bike_types = json.loads(place.attrib['bike_types'])
            for value in bike_types.values():
                try:
                    self.bikes += value
                except TypeError:
                    self.bikes += int(re.sub(r'\+$', '', value))
                    self.extra['bikes_approximate'] = True
        else:
            bikes = place.attrib['bikes']
            if bikes.endswith('+'):
                self.bikes = int(re.sub(r'\+$', '', bikes))
                self.extra['bikes_approximate'] = True
            else:
                self.bikes = int(bikes)

        if 'bike_racks' in place.attrib:
            self.free = int(place.attrib['free_racks'])
            self.extra['slots'] = int(place.attrib['bike_racks'])
        else:
            self.free = None

        if 'bike_numbers' in place.attrib:
            self.extra['bike_uids'] = place.attrib['bike_numbers'].split(',')
